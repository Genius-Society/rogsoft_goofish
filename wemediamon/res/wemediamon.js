var refresh_flag;
var count_down;
var _responseLen;
var _show_mon_log;

const chks = ["bilimon", "bilitsk", "hfmon", "gitmon", "cnblon", "itchion"]
const keys = ["email", "smtp", "cache", "period", "bilick", "hftks", "papers", "gitags", "cnblokie", "itck"];

function init() {
	show_menu(menu_hook);
	get_status();
	get_dbus_data();
	register_event();
	import_cfg();
}

function import_cfg() {
	document.getElementById('config').addEventListener('change', function (e) {
		const file = e.target.files[0];
		if (!file) return;
		const reader = new FileReader();
		reader.onload = evt => {
			try {
				const obj = JSON.parse(evt.target.result); // 解析成对象
				load_cfg(obj);
			} catch (err) {
				alert('配置文件格式错误', err);
			}
		};
		reader.readAsText(file); // 按文本读
	});
}

function load_cfg(obj) {
	keys.forEach(k => {
		if (k in obj) $(`#${k}`).val(obj[k]);
	});
	chks.forEach(k => {
		if (k in obj) $(`#${k}`).prop('checked', obj[k] == "on").trigger('change');;
	});
}

function export_cfg() {
	const data = {};
	for (const k of keys) data[k] = $(`#${k}`).val();
	for (const k of chks) data[k] = $(`#${k}`).val();
	const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
	const url = URL.createObjectURL(blob);
	$('<a>').attr({ href: url, download: 'wemediamon_cfg.json' }).appendTo('body')[0].click();
	URL.revokeObjectURL(url);
}

function register_event() {
	$(".popup_bar_bg_ks").click(function () { count_down = -1; });
	$(window).resize(function () {
		if ($('.popup_bar_bg_ks').css("visibility") == "visible") {
			document.scrollingElement.scrollTop = 0;
			var page_h = window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight;
			var page_w = window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth;
			var log_h = E("loadingBarBlock").clientHeight;
			var log_w = E("loadingBarBlock").clientWidth;
			var log_h_offset = (page_h - log_h) / 2;
			var log_w_offset = (page_w - log_w) / 2 + 90;
			$('#loadingBarBlock').offset({ top: log_h_offset, left: log_w_offset });
		}
	});
}

function show_hide_el(w) {
	if ($('.check_' + w).is(':checked')) {
		$('#table_' + w + ' tr:eq(0)').nextAll('tr').show();
	}
	else {
		$('#table_' + w + ' tr:eq(0)').nextAll('tr').hide();
	}
}

function show_hide(id) {
	if ($('#' + id).is(':checked')) {
		$('#' + id).nextAll('input[type=time]').show();
	}
	else {
		$('#' + id).nextAll('input[type=time]').hide();
	}
}

function conf2obj() {
	var count = 0;
	$('input[type="checkbox"][id]').each(function (_, el) {
		var id = $(el).attr("id");
		if (id && dbus["wemediamon_" + id]) {
			E(id).checked = (dbus["wemediamon_" + id] == "1");
			count++;
		}
	});
	for (var i = 0; i < count; i++) {
		show_hide_el(i);
	}

	$('textarea[name][id], input[type="text"][id], input[type="password"][id], input[type="number"][id]').each(function (_, el) {
		var id = $(el).attr("id");
		if (id && dbus["wemediamon_" + id]) {
			E(id).value = dbus["wemediamon_" + id];
		}
	});
}

function obj2conf(cmd) {
	var dbus_new = {};
	if (cmd == "WEB_SUBMIT") {
		$('input[type="checkbox"][id]').each(function (_, el) {
			var id = $(el).attr("id");
			if (id) {
				dbus_new["wemediamon_" + id] = E(id).checked ? '1' : '0';
			}
		});
	}
	else {
		get_run_log(1);
	}

	$('textarea[name][id], input[type="text"][id], input[type="password"][id], input[type="number"][id]').each(function (_, el) {
		var id = $(el).attr("id");
		if (id) {
			dbus_new["wemediamon_" + id] = E(id).value;;
		}
	});

	return dbus_new;
}

function get_dbus_data() {
	$.ajax({
		type: "GET",
		url: "/_api/wemediamon",
		dataType: "json",
		async: false,
		success: function (data) {
			dbus = data.result[0];
			conf2obj();
			register_event();
		}
	});
}

function get_status() {
	var id = parseInt(Math.random() * 100000000);
	var postData = { "id": id, "method": "wemediamon_status.sh", "params": [1], "fields": "" };
	$.ajax({
		type: "POST",
		cache: false,
		url: "/_api/",
		data: JSON.stringify(postData),
		dataType: "json",
		success: function (response) {
			if (response.result) {
				E("status").innerHTML = response.result;
				setTimeout("get_status();", 5000);
			}
		},
		error: function (xhr) {
			console.log(xhr)
			setTimeout("get_status();", 15000);
		}
	});
}

function get_run_log(flag) {
	E("ok_button").style.visibility = "hidden";
	showWBLoadingBar();
	$.ajax({
		url: '/_temp/wemediamon_run_log.txt',
		type: 'GET',
		cache: false,
		dataType: 'text',
		success: function (response) {
			var retArea = E("run_log_content");
			if (response.search("XU6J03M6") != -1) {
				retArea.value = response.replace("XU6J03M6", " ");
				E("ok_button").style.visibility = "visible";
				retArea.scrollTop = retArea.scrollHeight;
				if (flag == 1) {
					count_down = -1;
					refresh_flag = 0;
				} else {
					count_down = 6;
					refresh_flag = 1;
				}
				count_down_close();
				return false;
			}
			setTimeout("get_run_log(" + flag + ");", 200);
			retArea.value = response.replace("XU6J03M6", " ");
			retArea.scrollTop = retArea.scrollHeight;
		},
		error: function (err) {
			if (err.statusText == "Not Found") {
				E("loading_block_title").innerHTML = "当前日志为空 ...";
				E("run_log_content").value = "日志暂不存在, 点击确定关闭本窗口!";
			}
			else {
				E("loading_block_title").innerHTML = "获取日志异常 ...";
				E("run_log_content").value = "获取日志失败, 点击确定关闭本窗口!";
			}
			E("ok_button").style.visibility = "visible";
			return false;
		}
	});
}

function get_log() {
	if (_show_mon_log == 0) return;
	$.ajax({
		url: '/_temp/wemediamon_log.txt',
		type: 'GET',
		dataType: 'html',
		async: true,
		cache: false,
		success: function (response) {
			var retArea = E("log_content");
			if (_responseLen == response.length) {
				noChange++;
			} else {
				noChange = 0;
			}
			if (noChange > 10) {
				return false;
			} else {
				setTimeout("get_log();", 1500);
			}
			retArea.value = response;

			if ($(".stop_log").eq(0)[0].checked == false) {
				retArea.scrollTop = retArea.scrollHeight;
			}
			_responseLen = response.length;
		},
		error: function (err) {
			if (err.statusText == "Not Found") {
				E("log_pannel_title").innerHTML = "当前日志为空 ...";
				E("log_content").value = "日志暂不存在, 请返回主界面!";
			}
			else {
				E("log_pannel_title").innerHTML = "获取日志异常 ...";
				E("log_content").value = "获取日志失败, 请返回主界面!";
			}
			setTimeout("get_log();", 5000);
		}
	});
}

function trigger(cmd) {
	if (cmd) {
		var dbus_new = obj2conf(cmd);
		E("apply").disabled = true;
		var id = parseInt(Math.random() * 100000000);
		var postData = { "id": id, "method": "wemediamon_config.sh", "params": [cmd], "fields": dbus_new };
		$.ajax({
			type: "POST",
			url: "/_api/",
			data: JSON.stringify(postData),
			dataType: "json",
			success: function (_) {
				get_run_log(cmd != "WEB_SUBMIT");
				E("apply").disabled = false;
			}
		});
	}
}

function showWBLoadingBar() {
	document.scrollingElement.scrollTop = 0;
	E("loading_block_title").innerHTML = "应用中, 请稍后 ...";
	E("LoadingBar").style.visibility = "visible";
	var page_h = window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight;
	var page_w = window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth;
	var log_h = E("loadingBarBlock").clientHeight;
	var log_w = E("loadingBarBlock").clientWidth;
	var log_h_offset = (page_h - log_h) / 2;
	var log_w_offset = (page_w - log_w) / 2 + 90;
	$('#loadingBarBlock').offset({ top: log_h_offset, left: log_w_offset });
}

function hideWBLoadingBar() {
	E("LoadingBar").style.visibility = "hidden";
	E("ok_button").style.visibility = "hidden";
	if (refresh_flag == "1") {
		refreshpage();
	}
}

function count_down_close() {
	if (count_down == "0") {
		hideWBLoadingBar();
	}
	if (count_down < 0) {
		E("ok_btn").value = "手动关闭";
		return false;
	}
	E("ok_btn").value = "自动关闭(" + count_down + ")";
	--count_down;
	setTimeout("count_down_close();", 1000);
}

function show_mon_log() {
	document.scrollingElement.scrollTop = 0;
	E("log_pannel_title").innerHTML = "此处展示wemediamon程序的监控日志...";
	E("log_pannel_div").style.visibility = "visible";
	var page_h = window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight;
	var page_w = window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth;
	var log_h = E("log_pannel_table").clientHeight;
	var log_w = E("log_pannel_table").clientWidth;
	var log_h_offset = (page_h - log_h) / 2;
	var log_w_offset = (page_w - log_w) / 2;
	$('#log_pannel_table').offset({ top: log_h_offset, left: log_w_offset });
	_show_mon_log = 1;
	get_log();
}

function hide_log_pannel() {
	E("log_pannel_div").style.visibility = "hidden";
	_show_mon_log = 0;
}

function menu_hook(_, _) {
	tabtitle[tabtitle.length - 1] = new Array("", "WeMediaMon");
	tablink[tablink.length - 1] = new Array("", "Module_wemediamon.asp");
}

function tabSelect(w) {
	for (var i = 0; i <= 4; i++) {
		$('.show-btn' + i).removeClass('active');
		$('#tablet_' + i).hide();
	}
	$('.show-btn' + w).addClass('active');
	$('#tablet_' + w).show();
}
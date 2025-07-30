var refresh_flag;
var count_down;
var _responseLen;

function init() {
	show_menu(menu_hook);
	get_status();
	get_dbus_data();
	register_event();
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

function conf2obj() {
	$('input[type="checkbox"][id]').each(function (_, el) {
		var id = $(el).attr("id");
		if (id && dbus["wemediamon_" + id]) {
			E(id).checked = (dbus["wemediamon_" + id] == "1");
		}
	});

	$('input[type="text"][id]').each(function (_, el) {
		var id = $(el).attr("id");
		if (id && dbus["wemediamon_" + id]) {
			E(id).value = dbus["wemediamon_" + id];
		}
	});

	$('input[type="password"][id]').each(function (_, el) {
		var id = $(el).attr("id");
		if (id && dbus["wemediamon_" + id]) {
			E(id).value = dbus["wemediamon_" + id];
		}
	});

	$('textarea[name]').each(function (_, el) {
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
		get_log(1);
	}

	$('input[type="text"][id]').each(function (_, el) {
		var id = $(el).attr("id");
		if (id) {
			dbus_new["wemediamon_" + id] = E(id).value;;
		}
	});

	$('input[type="password"][id]').each(function (_, el) {
		var id = $(el).attr("id");
		if (id) {
			dbus_new["wemediamon_" + id] = E(id).value;;
		}
	});

	$('textarea[name]').each(function (_, el) {
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

function get_log(flag) {
	E("ok_button").style.visibility = "hidden";
	showWBLoadingBar();
	$.ajax({
		url: '/_temp/wemediamon_log.txt',
		type: 'GET',
		cache: false,
		dataType: 'text',
		success: function (response) {
			var retArea = E("log_content");
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
			setTimeout("get_log(" + flag + ");", 200);
			retArea.value = response.replace("XU6J03M6", " ");
			retArea.scrollTop = retArea.scrollHeight;
		},
		error: function (_) {
			E("loading_block_title").innerHTML = "暂无日志信息 ...";
			E("log_content").value = "日志文件为空, 请关闭本窗口!";
			E("ok_button").style.visibility = "visible";
			return false;
		}
	});
}

function get_run_log() {
	if (STATUS_FLAG == 0) return;
	$.ajax({
		url: '/_temp/wemediamon_run_log.txt',
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
				setTimeout("get_run_log();", 1500);
			}
			retArea.value = response;

			if (E("stop_log").checked == false) {
				retArea.scrollTop = retArea.scrollHeight;
			}
			_responseLen = response.length;
		},
		error: function (_) {
			E("log_pannel_title").innerHTML = "暂无日志信息 ...";
			E("log_content").value = "日志文件为空, 请关闭本窗口!";
			setTimeout("get_run_log();", 5000);
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
				get_log("WEB_SUBMIT" != cmd);
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

function show_log_pannel() {
	document.scrollingElement.scrollTop = 0;
	E("log_pannel_div").style.visibility = "visible";
	var page_h = window.innerHeight || document.documentElement.clientHeight || document.body.clientHeight;
	var page_w = window.innerWidth || document.documentElement.clientWidth || document.body.clientWidth;
	var log_h = E("log_pannel_table").clientHeight;
	var log_w = E("log_pannel_table").clientWidth;
	var log_h_offset = (page_h - log_h) / 2;
	var log_w_offset = (page_w - log_w) / 2;
	$('#log_pannel_table').offset({ top: log_h_offset, left: log_w_offset });
	STATUS_FLAG = 1;
	get_run_log();
}

function hide_log_pannel() {
	E("log_pannel_div").style.visibility = "hidden";
	STATUS_FLAG = 0;
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

function show_hide_el(w) {
	if ($('.check_' + w).is(':checked')) {
		$('#table_' + w + ' tr:eq(0)').nextAll('tr').show();
	}
	else {
		$('#table_' + w + ' tr:eq(0)').nextAll('tr').hide();
	}
}
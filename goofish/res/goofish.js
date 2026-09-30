var refresh_flag;
var count_down;
var _responseLen;
var _show_mon_log;

const module_count = 6;
const chks = [];
const keys = ["pass", "cache"];

function init() {
	show_menu(menu_hook);
	get_status();
	get_dbus_data();
	register_event();
	import_cfg();
}

function import_cfg() { // 导入配置
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

function load_cfg(obj) { // 加载配置
	keys.forEach(k => {
		if (k in obj) $(`#${k}`).val(obj[k]);
	});
	chks.forEach(k => {
		if (k in obj) $(`#${k}`).prop('checked', obj[k] == "on").trigger('change');
	});
}

function export_cfg() { // 导出配置
	const data = {};
	for (const k of keys) data[k] = $(`#${k}`).val();
	for (const k of chks) data[k] = $(`#${k}`).val();
	const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
	const url = URL.createObjectURL(blob);
	$('<a>').attr({ href: url, download: 'goofish_cfg.json' }).appendTo('body')[0].click();
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

function show_hide(el) { // 各面板开关显隐连动
	var w = Number($(el).attr('class').split("_")[1]);
	if (Number.isInteger(w)) {
		$('#table_' + w + ' tr:eq(' + Number(w == 2) + ')').nextAll('tr').toggle($('.check_' + w).is(':checked'));
	}
}

function filter_bili_ck(cookie) {
	let ck = cookie.trim();
	if (!ck) return "";
	const keepKeys = ["DedeUserID", "SESSDATA", "bili_jct", "buvid3"];
	const map = {};
	ck.split(";").forEach(item => {
		let [key, value] = item.trim().split("=");
		if (keepKeys.includes(key) && value) {
			map[key] = value;
		}
	});
	return keepKeys
		.filter(k => map[k])
		.map(k => `${k}=${map[k]}`)
		.join("; ");
}

function conf2obj() { // dbus 变量转控件值 
	$('input[type="checkbox"][id]').each(function (_, el) {
		var id = $(el).attr("id");
		if (id && dbus["goofish_" + id]) {
			E(id).checked = (dbus["goofish_" + id] == "1");
		}
		if ($(el).attr("onchange")) {
			show_hide(el);
		}
	});

	$('textarea[class][id][placeholder], input[type="text"][id], input[type="password"][id], input[type="number"][id], input[type="time"][id]').each(function (_, el) {
		var id = $(el).attr("id");
		if (id && dbus["goofish_" + id]) {
			E(id).value = dbus["goofish_" + id];
		}
	});
}

function obj2conf(cmd) { // 控件值转 dbus 变量
	var dbus_new = {};
	if (cmd == "WEB_SUBMIT") {
		$('input[type="checkbox"][id]').each(function (_, el) {
			var id = $(el).attr("id");
			if (id) {
				dbus_new["goofish_" + id] = E(id).checked ? '1' : '0';
			}
		});
	}
	else {
		get_run_log(1);
	}

	$('textarea[class][id][placeholder], input[type="text"][id], input[type="password"][id], input[type="number"][id], input[type="time"][id]').each(function (_, el) {
		var id = $(el).attr("id");
		if (id) {
			dbus_new["goofish_" + id] = id != "bilick" ? E(id).value.trim() : filter_bili_ck(E(id).value);
		}
	});

	return dbus_new;
}

function get_dbus_data() {
	$.ajax({
		type: "GET",
		url: "/_api/goofish",
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
	var postData = { "id": id, "method": "goofish_status.sh", "params": [1], "fields": "" };
	$.ajax({
		type: "POST",
		cache: false,
		url: "/_api/",
		data: JSON.stringify(postData),
		dataType: "json",
		success: function (response) {
			if (response.result) {
				E("kill").style.display = "none";
				E("status").innerHTML = response.result;
				setTimeout("get_status();", 5000);
			} else {
				E("kill").style.display = "unset";
			}
		},
		error: function (xhr) {
			console.log(xhr)
			setTimeout("get_status();", 15000);
			E("kill").style.display = "unset";
		}
	});
}

function get_run_log(flag) {
	E("ok_button").style.visibility = "hidden";
	showWBLoadingBar();
	$.ajax({
		url: '/_temp/goofish_run_log.txt',
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
		url: '/_temp/goofish_log.txt',
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
		var postData = { "id": id, "method": "goofish_config.sh", "params": [cmd], "fields": dbus_new };
		$.ajax({
			type: "POST",
			url: "/_api/",
			data: JSON.stringify(postData),
			dataType: "json",
			success: function (_) {
				get_run_log(!(cmd == "WEB_SUBMIT" || cmd == "CHK_UPD"));
				E("apply").disabled = false;
			}
		});
	}
}

function kill() {
	var id = parseInt(Math.random() * 100000000);
	var postData = {
		"id": id,
		"method": "goofish_config.sh",
		"params": ["FORCE_STOP"],
		"fields": {}
	};
	$.ajax({
		type: "POST",
		url: "/_api/",
		data: JSON.stringify(postData),
		dataType: "json",
		success: function (resp) {
			E("apply").disabled = false;
			console.log("FORCE_STOP done:", resp);
			setTimeout("get_status();", 1000);// 只做静默刷新，不弹日志窗
		},
		error: function (err) {
			E("apply").disabled = false;
			console.log("FORCE_STOP failed:", err);
		}
	});
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
	if (refresh_flag == "1") refreshpage();
}

function count_down_close() {
	if (count_down == "0") hideWBLoadingBar();
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
	E("log_pannel_title").innerHTML = "此处展示goofish程序的监控日志...";
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
	tabtitle[tabtitle.length - 1] = new Array("", "goofish");
	tablink[tablink.length - 1] = new Array("", "Module_goofish.asp");
}

function tabSelect(w) {
	for (var i = 0; i < module_count; i++) {
		$('.show-btn' + i).removeClass('active');
		$('#tablet_' + i).hide();
	}
	$('.show-btn' + w).addClass('active');
	$('#tablet_' + w).show();
}

function hint(itemNum) {
	_caption = "";
	statusmenu = "";
	width = "350px";
	if (itemNum == 1) {
		_caption = "插件版本信息";
		statusmenu = "点击“开发日志”按钮可查看当前插件在 GitHub 上的开发日志信息; 点击“检查更新”按钮可检查插件是否有更新, 若发现更新则自动更新插件。<br>";
	}
	if (itemNum == 2) {
		_caption = "插件总开关";
		statusmenu = "点击“监控日志”按钮可查看当前插件所有日志信息。<br>";
	}
	else if (itemNum == 3) {
		_caption = "当前插件 Python 主程序实时运行状态信息";
		statusmenu = "点击“执行日志”按钮可查看最新手动单次触发执行指令的日志信息。<br>";
	}
	else if (itemNum == 4) {
		_caption = "闲鱼智能自动发货与管家系统管理员密码";
		statusmenu = "不要空着, 输入要修改的密码后, 点击“密码重置”即可生效。<br>";
	}
	else if (itemNum == 5) {
		_caption = "访问闲鱼控制台";
		statusmenu = "点击“访问闲鱼面板”按钮，将在新标签页中打开插件提供的 Web 控制台 (默认地址 http://router.asus.com:8080)。您可以在控制台中管理闲鱼账号、查看运行日志、调整各媒体面板设置以及执行其他高级操作。建议将地址保存为书签, 方便日后快速访问; 点击“环境修复”按钮可修复 pip 依赖环境。<br>";
	}

	return overlib(statusmenu, OFFSETX, 10, OFFSETY, 10, RIGHT, STICKY, WIDTH, 'width', CAPTION, _caption, CLOSETITLE, '');
}
var refresh_flag;
var count_down;
var _responseLen;
var _show_mon_log;

const chks = ["bilimon", "hfmon", "gitmon", "cnblon", "itchion"]
const keys = ["email", "smtp", "cache", "period", "bilick", "btskon", "btskat", "bcoinon", "bcoinat", "hftks", "papers", "gitags", "cnblokie", "itck"];

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

function show_hide(w) { // 各面板开关显隐连动
	if ($('.check_' + w).is(':checked')) {
		$('#table_' + w + ' tr:eq(0)').nextAll('tr').show();
	}
	else {
		$('#table_' + w + ' tr:eq(0)').nextAll('tr').hide();
	}
}

function show_hide_el(el) {
	if ($(el).is(':checked')) {
		$(el).next('div').show();
	}
	else {
		$(el).next('div').hide();
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
	var i = 0;
	$('input[type="checkbox"][id]').each(function (_, el) {
		var id = $(el).attr("id");
		if (id && dbus["wemediamon_" + id]) {
			E(id).checked = (dbus["wemediamon_" + id] == "1");
		}
		if ($(el).attr("onchange")) {
			show_hide(i);
			i++;
		}
	});

	$('textarea[class][id][placeholder], input[type="text"][id], input[type="password"][id], input[type="number"][id], input[type="time"][id]').each(function (_, el) {
		var id = $(el).attr("id");
		if (id && dbus["wemediamon_" + id]) {
			E(id).value = dbus["wemediamon_" + id];
		}
	});
}

function obj2conf(cmd) { // 控件值转 dbus 变量
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

	$('textarea[class][id][placeholder], input[type="text"][id], input[type="password"][id], input[type="number"][id], input[type="time"][id]').each(function (_, el) {
		var id = $(el).attr("id");
		if (id) {
			dbus_new["wemediamon_" + id] = id != "bilick" ? E(id).value.trim() : filter_bili_ck(E(id).value);
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

function hint(itemNum) {
	_caption = "";
	statusmenu = "";
	width = "350px";
	if (itemNum == 0.1) {
		_caption = "插件总开关";
		statusmenu = "点击“监控日志”按钮可查看当前插件所有日志信息。<br>";
	}
	else if (itemNum == 0.2) {
		_caption = "当前插件 Python 主程序实时运行状态信息";
		statusmenu = "点击“执行日志”按钮可查看最新手动单次触发执行指令的日志信息。<br>";
	}
	else if (itemNum == 0.3) {
		_caption = "用于接收插件重要级提示的 QQ 系邮箱";
		statusmenu = "支持邮箱后缀域有：@qq.com、@foxmail.com、@vip.qq.com。<br>";
	}
	else if (itemNum == 0.4) {
		_caption = "用于接收插件重要级提示的 QQ 系邮箱的 SMTP 应用密钥";
		statusmenu = "浏览器登陆 QQ 邮箱后进入“账号与安全-安全设置”, 找到“POP3/IMAP/SMTP/Exchange/CardDAV 服务”, 点击“生成授权码”获取; 点击“邮件测试”按钮可测试提示邮箱有效性。<br>";
	}
	else if (itemNum == 0.5) {
		_caption = "插件产生的缓存文件在路由器本地的储存路径";
		statusmenu = "请填写路由器本地存在且容量足够可写入的路径; 点击“环境修复”按钮可修复 pip 依赖环境。<br>"
	}
	else if (itemNum == 0.6) {
		_caption = "插件监控器的刷新周期";
		statusmenu = "以小时为单位, 默认值为2小时, 即每2小时触发一次。<br>";
	}
	else if (itemNum == 0.7) {
		_caption = "一键导入插件的整体配置";
		statusmenu = "包含 WeMediaMon 设定及下属各自媒体面板设置, 仅支持导入本插件导出的 json 格式配置文件; 点击“导出配置”按钮可将插件当前整体配置状态导出为单个 json 配置文件。<br>";
	}
	else if (itemNum == 1.1) {
		_caption = "B站自媒体面板总开关";
		statusmenu = "选中后为打开状态, 且后续隐藏折叠内容会自动显示。<br>";
	}
	else if (itemNum == 1.2) {
		_caption = "被监控B站账号的 Cookie 缓存值";
		statusmenu = "获取方式：浏览器打开“开发者工具-网络”, 查看已登陆状态B站请求标头, 拷贝 Cookie 值至此。1年长生存期 Cookie 获取走 passport.bilibili.com 协议登录; 7天短生存期的走B站主页 Web 登录, 但需配合下面每日签到的 AC 时间值协同使用。<br>";
	}
	else if (itemNum == 1.3) {
		_caption = "B站自动完成每日任务功能";
		statusmenu = "左侧 checkbox 未选中则不开启; 右侧时间选择框内为每日签到的触发时间。<br>";
	}
	else if (itemNum == 1.4) {
		_caption = "B站自动完成每日投币功能";
		statusmenu = "左侧输入框填入触发周期天数才可开启, 置 0 则不开启; 右侧时间选择框内为投币的触发时间。<br>";
	}
	else if (itemNum == 2.1) {
		_caption = "HuggingFace 自媒体面板总开关";
		statusmenu = "选中后为打开状态, 且后续隐藏折叠内容会自动显示。<br>";
	}
	else if (itemNum == 2.2) {
		_caption = "HuggingFace 组织管理员账号的 Token 密钥令牌";
		statusmenu = "登录状态下可在 https://huggingface.co/settings/tokens 页面创建, 创建时一定要勾选个人和被管理组织的 Repositories 权限, 若填写多个账号 Token 需以;隔开。<br>";
	}
	else if (itemNum == 2.3) {
		_caption = "HuggingFace 上被监控的 arXiv 论文编号";
		statusmenu = "格式为 XXXX.XXXXX, 若填写多个需以;隔开。<br>";
	}
	else if (itemNum == 3.1) {
		_caption = "GitHub 自媒体面板总开关";
		statusmenu = "选中后为打开状态, 且后续隐藏折叠内容会自动显示。<br>";
	}
	else if (itemNum == 3.2) {
		_caption = "被监控的 GitHub 用户名";
		statusmenu = "多个'用户名'或'用户名/仓库名'(可共存)需以;隔开。<br>";
	}
	else if (itemNum == 4.1) {
		_caption = "博客园自媒体面板总开关";
		statusmenu = "选中后为打开状态, 且后续隐藏折叠内容会自动显示。<br>";
	}
	else if (itemNum == 4.2) {
		_caption = "被监控博客园账号的 Cookie 缓存值";
		statusmenu = "获取方式：浏览器打开“开发者工具-网络”, 查看已登陆状态博客园主页请求标头, 拷贝 Cookie 值至此。<br>";
	}
	else if (itemNum == 5.1) {
		_caption = "itch.io 自媒体面板总开关";
		statusmenu = "选中后为打开状态, 且后续隐藏折叠内容会自动显示。<br>";
	}
	else if (itemNum == 5.2) {
		_caption = "被监控 itch.io 账号的 Cookie 缓存值";
		statusmenu = "获取方式：浏览器打开“开发者工具-网络”, 查看已登陆状态下 https://itch.io/my-followers 页面请求标头, 拷贝 Cookie 值至此。<br>";
	}

	return overlib(statusmenu, OFFSETX, 10, OFFSETY, 10, RIGHT, STICKY, WIDTH, 'width', CAPTION, _caption, CLOSETITLE, '');
}
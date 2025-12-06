var refresh_flag;
var count_down;
var _responseLen;
var _show_mon_log;

const chks = ["bilimon", "btskon", "hfmon", "gitmon", "cnblon", "itchion"]
const keys = ["email", "smtp", "cache", "period", "bilick", "btskat", "hftks", "papers", "gitags", "cnblokie", "itck"];

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
		if (k in obj) $(`#${k}`).prop('checked', obj[k] == "on").trigger('change');;
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

function open_wemediamon_hint(itemNum) {
	statusmenu = "";
	width = "350px";
	if (itemNum == 0.1) {
		statusmenu = "&nbsp;&nbsp;&nbsp;&nbsp;1. 此处填写cloudreve二进制程序在路由器后台的部署位置。请注意: 部署位置的存储容量将直接影响到cloudreve网盘的容量上限, 建议将目录位置设置在路由器USB挂载的外置大容量存储设备中!<br/><br/>"
		statusmenu += "&nbsp;&nbsp;&nbsp;&nbsp;2. 该目录将承载所有cloudreve用户的上传文件, 因此网盘使用久了若修改该路径将会牵一发而动全身, 还请谨慎操作。<br/><br/>"
		statusmenu += "&nbsp;&nbsp;&nbsp;&nbsp;3. 卸载插件不会清理此目录, 可用SSH连入路由器或使用FileBrowser插件等方法进入该路径手动下载备份或清除用户数据。<br/><br/>"
		_caption = "部署目录";
	}
	if (itemNum == 0.2) {
		statusmenu = "&nbsp;&nbsp;&nbsp;&nbsp;1. 此处显示cloudreve二进制程序在路由器后台的简要运行情况, 详细运行日志可以点击顶部的<b>cloudreve运行日志</b>查看。<br/><br/>"
		statusmenu += "&nbsp;&nbsp;&nbsp;&nbsp;2. 当开启了实时进程守护后, 可以看到cloudreve二进制运行时长, 即守护运行时间。<br/><br/>"
		statusmenu += "&nbsp;&nbsp;&nbsp;&nbsp;3. 当出现<b>获取运行状态失败</b>时, 可能是路由器后台登陆超时或者httpd进程崩溃导致, 如果是后者, 请等待路由器httpd进程恢复, 或者自行使用ssh命令: server restart_httpd重启httpd。<br/><br/>"
		_caption = "运行状态";
	}
	if (itemNum == 2) {
		statusmenu = "&nbsp;&nbsp;&nbsp;&nbsp;1. 此处显示cloudreve二进制程序的版本号及其内置的cloudreve面板版本号。<br/><br/>"
		statusmenu += "&nbsp;&nbsp;&nbsp;&nbsp;2. cloudreve二进制程序下载自cloudreve的github项目release页面的cloudreve-linux-arm64版本。<br/><br/>"
		statusmenu += "&nbsp;&nbsp;&nbsp;&nbsp;3.目前只支持hnd机型中的armv8机型, 比如cpu型号为BCM4906、BCM4908、BCM4912等armv8机型。<br/><br/>"
		_caption = "运行状态";
	}
	if (itemNum == 4) {
		width = "780px";
		statusmenu = "&nbsp;&nbsp;&nbsp;&nbsp;在不同的配置和网络环境下, 点击【访问Cloudreve面板】进入的是不同地址: ";
		statusmenu += "<br/><br/>";
		statusmenu += "1️⃣<font color='#F00'>局域网访问 (http) </font><br/>";
		statusmenu += "&nbsp;&nbsp;&nbsp;&nbsp;1. cloudreve插件内: 关闭公网访问<br/>";
		statusmenu += "&nbsp;&nbsp;&nbsp;&nbsp;2. 开启cloudreve插件<br/>";
		statusmenu += "&nbsp;&nbsp;&nbsp;&nbsp;3. 此时点击【访问Cloudreve面板】就是访问局域网地址: https://192.168.50.1:5212, 或: http://router.asus.com:5212";
		statusmenu += "<br/><br/>";
		statusmenu += "2️⃣<font color='#F00'>公网ddns访问 (http) </font><br/>";
		statusmenu += "&nbsp;&nbsp;&nbsp;&nbsp;0. 路由器已经配置了ddns, 如域名 ax86.ddns.com 解析到路由器的公网ip<br/>";
		statusmenu += "&nbsp;&nbsp;&nbsp;&nbsp;1. cloudreve插件内: 开启公网访问<br/>";
		statusmenu += "&nbsp;&nbsp;&nbsp;&nbsp;2. cloudreve插件内: 关闭https<br/>";
		statusmenu += "&nbsp;&nbsp;&nbsp;&nbsp;3. cloudreve插件内: 网站URL可以不填写, 或者填 http://ax86.ddns.com:5212<br/>";
		statusmenu += "&nbsp;&nbsp;&nbsp;&nbsp;4. 开启cloudreve插件<br/>";
		statusmenu += "&nbsp;&nbsp;&nbsp;&nbsp;5. 网站URL不填的话, 此时点击【访问Cloudreve面板】就是访问局域网地址: http://192.168.50.1:5212<br/>";
		statusmenu += "&nbsp;&nbsp;&nbsp;&nbsp;6. 网站URL要填的话, 填: http://ax86.ddns.com:5212, 此时点击【访问Cloudreve面板】就是通过填写的url访问";
		statusmenu += "<br/><br/>";
		statusmenu += "3️⃣<font color='#F00'>公网ddns访问 (https) </font><br/>";
		statusmenu += "&nbsp;&nbsp;&nbsp;&nbsp;0. 路由器已经配置了ddns, 如域名 ax86.ddns.com, 且配置了https证书<br/>";
		statusmenu += "&nbsp;&nbsp;&nbsp;&nbsp;1. cloudreve插件内: 开启公网访问<br/>";
		statusmenu += "&nbsp;&nbsp;&nbsp;&nbsp;2. cloudreve插件内: 开启https, 证书公钥填/etc/cert.pem, 证书私钥填: /etc/key.pem<br/>";
		statusmenu += "&nbsp;&nbsp;&nbsp;&nbsp;3. cloudreve插件内: 网站URL可以不填写, 或者填https://ax86.ddns.com:5212<br/>";
		statusmenu += "&nbsp;&nbsp;&nbsp;&nbsp;4. 开启cloudreve插件<br/>";
		statusmenu += "&nbsp;&nbsp;&nbsp;&nbsp;5. 网站URL不填的话, 此时点击【访问Cloudreve面板】就是访问局域网地址: https://192.168.50.1:5212, 不过会提示证书不安全<br/>";
		statusmenu += "&nbsp;&nbsp;&nbsp;&nbsp;6. 网站URL要填的话, 填: https://ax86.ddns.com:5212, 此时点击【访问Cloudreve面板】就是通过填写的url访问<br/>";
		statusmenu += "&nbsp;&nbsp;&nbsp;&nbsp;7. 注意开启https后, 所有http的访问方式将失效";
		statusmenu += "<br/><br/>";
		statusmenu += "4️⃣<font color='#F00'>ddnsto穿透访问</font><br/>";
		statusmenu += "&nbsp;&nbsp;&nbsp;&nbsp;0. 路由器已经配置了ddnsto, 如域名 ax86.ddnsto.com<br/>";
		statusmenu += "&nbsp;&nbsp;&nbsp;&nbsp;1. cloudreve插件内: 关闭公网访问关<br/>";
		statusmenu += "&nbsp;&nbsp;&nbsp;&nbsp;2. ddnsto后台配置主域名: ax86-cloudreve, ax86要换成自己的主域名<br/>";
		statusmenu += "&nbsp;&nbsp;&nbsp;&nbsp;3. ddnsto后台配置目标主机地址: http://192.168.60.1:5212<br/>";
		statusmenu += "&nbsp;&nbsp;&nbsp;&nbsp;4. 开启cloudreve插件<br/>";
		statusmenu += "&nbsp;&nbsp;&nbsp;&nbsp;5. 此时点击【访问Cloudreve面板】就是访问ddnsto地址: https://ax86-cloudreve.ddnsto.com<br/>";
		statusmenu += "&nbsp;&nbsp;&nbsp;&nbsp;6. 你也可以开启公网访问后填写https://ax86-cloudreve.ddnsto.com到网站URL";
		statusmenu += "</div>";
		_caption = "说明: ";
		return overlib(statusmenu, OFFSETX, -160, OFFSETY, 10, RIGHT, STICKY, WIDTH, 'width', CAPTION, _caption, CLOSETITLE, '');
	}
	if (itemNum == 5) {
		statusmenu = "&nbsp;&nbsp;&nbsp;&nbsp;采用perp对cloudreve进程进行实时进程守护, 这比一些定时检查脚本更有效率, 当然如果cloudreve程序在你的路由器上运行良好, 完全可以不使用进程守护。"
		statusmenu += "<br/><br/>&nbsp;&nbsp;&nbsp;&nbsp;由于cloudreve对路由器资源占用较多, 所以强烈建议为路由器配置1G及以上的虚拟内存, 以保证cloudreve的稳定运行!"
		_caption = "实时进程守护";
	}
	if (itemNum == 6) {
		statusmenu = "&nbsp;&nbsp;&nbsp;&nbsp;开启公网访问后, cloudreve将监听在0.0.0.0地址, 这样就能从WAN外部访问路由器内的cloudreve面板。<br/><br/>"
		statusmenu += "&nbsp;&nbsp;&nbsp;&nbsp;关闭公网访问后, cloudreve将监听在局域网地址如: 192.168.50.1上, 这样cloudreve面板仅能从局域网内部访问, "
		_caption = "开启公网访问";
	}
	if (itemNum == 7) {
		statusmenu = "&nbsp;&nbsp;&nbsp;&nbsp;cloudreve面板默认端口为5212, 你可以自行更改为其它端口。请注意: 如果你需要配置webdav, 同样应该使用该端口!。<br/><br/>"
		_caption = "面板端口";
	}
	if (itemNum == 8) {
		statusmenu = "&nbsp;&nbsp;&nbsp;&nbsp;cloudreve面板默认端口为5213, 你可以自行更改为其它端口。请注意: 如果你需要配置webdav, 同样应该使用该端口!。<br/><br/>"
		_caption = "面板端口";
	}
	if (itemNum == 9) {
		width = "690px";
		statusmenu = "1️⃣只有当开启公网访问时才能启用https, 且建议路由器已经配置了DDNS + https证书的情况下才启用https选项!<br/><br/>";
		statusmenu += "2️⃣启用https后, 下面的<b>证书公钥Cert文件</b>和<b>证书私钥Key文件</b>选项也必须正确填写, 才能起作用!<br/><br/>";
		statusmenu += "3️⃣https启用成功后, 后台面板就无法使用http地址进行访问了!<br/><br/>";
		statusmenu += "4️⃣如果你为路由器配置了DDNS和https证书, cloudreve可以使用相同的证书, 即: <br/>";
		statusmenu += "&nbsp;&nbsp;&nbsp;&nbsp;证书Cert文件路径(绝对路径): <font color='#CC0066'>/etc/cert.pem</font><br/>";
		statusmenu += "&nbsp;&nbsp;&nbsp;&nbsp;证书Key文件路径(绝对路径): <font color='#CC0066'>/etc/key.pem</font><br/><br/>";
		statusmenu += "5️⃣如果你使用ddnsto内网穿透服务, 请不要开启https选项!<br/><br/>";
		_caption = "启用https: ";
		return overlib(statusmenu, OFFSETX, -30, OFFSETY, 10, RIGHT, STICKY, WIDTH, 'width', CAPTION, _caption, CLOSETITLE, '');
	}
	if (itemNum == 10) {
		statusmenu = "&nbsp;&nbsp;&nbsp;&nbsp;开启系统检测功能可以防止因对路由器性能理解不足而出现的各种异常情况"
		statusmenu += "<br/><br/>&nbsp;&nbsp;&nbsp;&nbsp;如果关闭系统检测，请确保可以理解并能处理路由器出现的各种异常情况"
		statusmenu += "<br/><br/>&nbsp;&nbsp;&nbsp;&nbsp;目前检测项目："
		statusmenu += "<br/><br/>&nbsp;&nbsp;&nbsp;&nbsp;内存大小和虚拟内存挂载情况 (物理内存低于1G, 强制挂载虚拟内存) "
		statusmenu += "<br/><br/>&nbsp;&nbsp;&nbsp;&nbsp;已开启插件检测并提示"
		statusmenu += "<br/><br/>&nbsp;&nbsp;&nbsp;&nbsp;由于cloudreve对路由器资源占用较多, 所以强烈建议为路由器配置1G及以上的虚拟内存, 以保证cloudreve的稳定运行!"
		_caption = "关闭系统检测";
	}

	return overlib(statusmenu, OFFSETX, 10, OFFSETY, 10, RIGHT, STICKY, WIDTH, 'width', CAPTION, _caption, CLOSETITLE, '');
}

function mOver(obj, hint) {
	$(obj).css({
		"color": "#00ffe4",
		"text-decoration": "underline"
	});
	open_wemediamon_hint(hint);
}

function mOut(obj) {
	$(obj).css({
		"color": "#fff",
		"text-decoration": ""
	});
	E("overDiv").style.visibility = "hidden";
}
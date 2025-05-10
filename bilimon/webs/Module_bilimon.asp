<!DOCTYPE html
    PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">

<head>
    <meta http-equiv="X-UA-Compatible" content="IE=Edge" />
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <meta HTTP-EQUIV="Pragma" CONTENT="no-cache" />
    <meta HTTP-EQUIV="Expires" CONTENT="-1" />
    <link rel="shortcut icon" href="images/favicon.png" />
    <link rel="icon" href="images/favicon.png" />
    <title>软件中心 - BiliMon</title>
    <link rel="stylesheet" type="text/css" href="index_style.css" />
    <link rel="stylesheet" type="text/css" href="form_style.css" />
    <link rel="stylesheet" type="text/css" href="css/element.css">
    <link rel="stylesheet" type="text/css" href="/res/softcenter.css">
    <link rel="stylesheet" type="text/css" href="/res/layer/theme/default/layer.css">
    <script language="JavaScript" type="text/javascript" src="/js/jquery.js"></script>
    <script type="text/javascript" src="/res/Browser.js"></script>
    <script type="text/javascript" src="/res/softcenter.js"></script>
    <script type="text/javascript" src="/state.js"></script>
    <script type="text/javascript" src="/general.js"></script>
    <script type="text/javascript" src="/popup.js"></script>
    <style>
        a:focus {
            outline: none;
        }

        .FormTitle i {
            color: #ff002f;
            font-style: normal;
        }

        .SimpleNote {
            padding: 5px 10px;
        }

        .popup_bar_bg_ks {
            position: fixed;
            margin: auto;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 99;
            filter: alpha(opacity=90);
            background-repeat: repeat;
            visibility: hidden;
            overflow: hidden;
            background: rgba(68, 79, 83, 0.85) none repeat scroll 0 0 !important;
            background-position: 0 0;
            background-size: cover;
            opacity: .94;
        }

        .loadingBarBlock {
            width: 740px;
        }

        .loading_block_spilt {
            background: #656565;
            height: 1px;
            width: 98%;
        }

        #bilimon_main {
            border-width: 0.5px;
        }

        #bilimon_feat_cookie,
        #bilimon_feat_cookie2 {
            -webkit-text-security: square;
        }

        #bilimon_feat_cookie:focus,
        #bilimon_feat_cookie2:focus {
            -webkit-text-security: none;
        }
    </style>
    <script>
        var odm = '<% nvram_get("productid"); %>'
        var lan_ipaddr = "<% nvram_get(lan_ipaddr); %>"
        var params_chk = ['bilimon_enable'];
        var params_inp = [];
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
            $(".popup_bar_bg_ks").click(function () {
                count_down = -1;
            });
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

        function get_dbus_data() {
            $.ajax({
                type: "GET",
                url: "/_api/bilimon",
                dataType: "json",
                async: false,
                success: function (data) {
                    dbus = data.result[0];
                    conf2obj();
                    register_event();
                }
            });
        }

        function conf2obj() {
            for (var i = 0; i < params_chk.length; i++) {
                if (dbus[params_chk[i]]) {
                    E(params_chk[i]).checked = dbus[params_chk[i]] != "0";
                }
            }
            if (dbus["bilimon_period"]) {
                E("bilimon_feat_period").value = dbus["bilimon_period"]
            }
            if (dbus["bilimon_mail"]) {
                E("bilimon_feat_mail").value = dbus["bilimon_mail"]
            }
            if (dbus["bilimon_smtp"]) {
                E("bilimon_feat_smtp").value = dbus["bilimon_smtp"]
            }
            if (dbus["bilimon_tmp"]) {
                E("bilimon_feat_tmp").value = dbus["bilimon_tmp"]
            }
            if (dbus["bilimon_cookie"]) {
                E("bilimon_feat_cookie").value = dbus["bilimon_cookie"]
            }
            if (dbus["bilimon_cookie2"]) {
                E("bilimon_feat_cookie2").value = dbus["bilimon_cookie2"]
            }
        }

        function get_status() {
            var id = parseInt(Math.random() * 100000000);
            var postData = { "id": id, "method": "bilimon_status.sh", "params": [1], "fields": "" };
            $.ajax({
                type: "POST",
                cache: false,
                url: "/_api/",
                data: JSON.stringify(postData),
                dataType: "json",
                success: function (response) {
                    if (response.result) {
                        E("bilimon_status").innerHTML = response.result;
                        setTimeout("get_status();", 5000);
                    }
                },
                error: function (xhr) {
                    console.log(xhr)
                    setTimeout("get_status();", 15000);
                }
            });
        }

        function trigger(mode) {
            var trigger_mode = "";
            switch (mode) {
                case 1:
                    trigger_mode = "trigger_once";
                    break;
                case 2:
                    trigger_mode = "trigger_clean";
                    break;
                case 3:
                    trigger_mode = "smtp_test";
                    break;
                default:
                    break;
            }
            if (trigger_mode != "") {
                get_log(1);
                var dbus_new = {};
                dbus_new["bilimon_period"] = E("bilimon_feat_period").value;
                dbus_new["bilimon_mail"] = E("bilimon_feat_mail").value;
                dbus_new["bilimon_smtp"] = E("bilimon_feat_smtp").value;
                dbus_new["bilimon_tmp"] = E("bilimon_feat_tmp").value;
                dbus_new["bilimon_cookie"] = E("bilimon_feat_cookie").value;
                dbus_new["bilimon_cookie2"] = E("bilimon_feat_cookie2").value;
                E("bilimon_apply").disabled = true;
                var id = parseInt(Math.random() * 100000000);
                var postData = { "id": id, "method": "bilimon_config.sh", "params": [trigger_mode], "fields": dbus_new };
                $.ajax({
                    type: "POST",
                    url: "/_api/",
                    data: JSON.stringify(postData),
                    dataType: "json",
                    success: function (response) {
                        get_log(1);
                        E("bilimon_apply").disabled = false;
                    }
                });
            }
        }

        function watchdog() {
            get_log(1);
            var dbus_new = {};
            dbus_new["bilimon_tmp"] = E("bilimon_feat_tmp").value;
            E("bilimon_apply").disabled = true;
            var id = parseInt(Math.random() * 100000000);
            var postData = { "id": id, "method": "bilimon_config.sh", "params": ["watch_dogs"], "fields": dbus_new };
            $.ajax({
                type: "POST",
                url: "/_api/",
                data: JSON.stringify(postData),
                dataType: "json",
                success: function (response) {
                    get_log(1);
                    E("bilimon_apply").disabled = false;
                }
            });
        }

        function fixenv() {
            get_log(1);
            var dbus_new = {};
            dbus_new["bilimon_tmp"] = E("bilimon_feat_tmp").value;
            E("bilimon_apply").disabled = true;
            var id = parseInt(Math.random() * 100000000);
            var postData = { "id": id, "method": "bilimon_config.sh", "params": ["fix_env"], "fields": dbus_new };
            $.ajax({
                type: "POST",
                url: "/_api/",
                data: JSON.stringify(postData),
                dataType: "json",
                success: function (response) {
                    get_log(1);
                    E("bilimon_apply").disabled = false;
                }
            });
        }

        function save() {
            var dbus_new = {};
            for (var i = 0; i < params_chk.length; i++) {
                dbus_new[params_chk[i]] = E(params_chk[i]).checked ? '1' : '0';
            }
            dbus_new["bilimon_period"] = E("bilimon_feat_period").value;
            dbus_new["bilimon_mail"] = E("bilimon_feat_mail").value;
            dbus_new["bilimon_smtp"] = E("bilimon_feat_smtp").value;
            dbus_new["bilimon_tmp"] = E("bilimon_feat_tmp").value;
            dbus_new["bilimon_cookie"] = E("bilimon_feat_cookie").value;
            dbus_new["bilimon_cookie2"] = E("bilimon_feat_cookie2").value;
            E("bilimon_apply").disabled = true;
            var id = parseInt(Math.random() * 100000000);
            var postData = { "id": id, "method": "bilimon_config.sh", "params": ["web_submit"], "fields": dbus_new };
            $.ajax({
                type: "POST",
                url: "/_api/",
                data: JSON.stringify(postData),
                dataType: "json",
                success: function (response) {
                    E("bilimon_apply").disabled = false;
                    get_log();
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
            if (refresh_flag == "1") {
                refreshpage();
            }
        }

        function count_down_close() {
            if (count_down == "0") {
                hideWBLoadingBar();
            }
            if (count_down < 0) {
                E("ok_button1").value = "手动关闭"
                return false;
            }
            E("ok_button1").value = "自动关闭(" + count_down + ")"
            --count_down;
            setTimeout("count_down_close();", 1000);
        }

        function get_log(flag) {
            E("ok_button").style.visibility = "hidden";
            showWBLoadingBar();
            $.ajax({
                url: '/_temp/bilimon_log.txt',
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
                error: function (xhr) {
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
                url: '/_temp/bilimon_run_log.txt',
                type: 'GET',
                dataType: 'html',
                async: true,
                cache: false,
                success: function (response) {
                    var retArea = E("log_content_bilimon");
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

                    if (E("bilimon_stop_log").checked == false) {
                        retArea.scrollTop = retArea.scrollHeight;
                    }
                    _responseLen = response.length;
                },
                error: function (xhr) {
                    E("log_pannel_title").innerHTML = "暂无日志信息 ...";
                    E("log_content_bilimon").value = "日志文件为空, 请关闭本窗口!";
                    setTimeout("get_run_log();", 5000);
                }
            });
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

        function menu_hook(title, tab) {
            tabtitle[tabtitle.length - 1] = new Array("", "BiliMon");
            tablink[tablink.length - 1] = new Array("", "Module_bilimon.asp");
        }
    </script>
</head>

<body onload="init();">
    <div id="TopBanner"></div>
    <div id="Loading" class="popup_bg"></div>
    <div id="LoadingBar" class="popup_bar_bg_ks" style="z-index: 200;">
        <table cellpadding="5" cellspacing="0" id="loadingBarBlock" class="loadingBarBlock" align="center">
            <tr>
                <td height="100">
                    <div id="loading_block_title" style="margin:10px auto;margin-left:10px;width:85%; font-size:12pt;">
                    </div>
                    <div id="loading_block_spilt" style="margin:10px 0 10px 5px;" class="loading_block_spilt"></div>
                    <div style="margin-left:15px;margin-right:15px;margin-top:10px;overflow:hidden">
                        <textarea cols="50" rows="25" wrap="off" readonly="readonly" id="log_content" autocomplete="off"
                            autocorrect="off" autocapitalize="off" spellcheck="false"
                            style="border:1px solid #000;width:99%; font-family:'Lucida Console'; font-size:11px;background:transparent;color:#FFFFFF;outline: none;padding-left:3px;padding-right:22px;overflow-x:hidden"></textarea>
                    </div>
                    <div id="ok_button" class="apply_gen" style="background:#000;visibility:hidden;">
                        <input id="ok_button1" class="button_gen" type="button" onclick="hideWBLoadingBar()" value="确定">
                    </div>
                </td>
            </tr>
        </table>
    </div>
    <div id="log_pannel_div" class="popup_bar_bg_ks" style="z-index: 200;">
        <table cellpadding="5" cellspacing="0" id="log_pannel_table" class="loadingBarBlock" style="width:960px"
            align="center">
            <tr>
                <td height="100">
                    <div style="text-align: center;font-size: 18px;color: #99FF00;padding: 10px;font-weight: bold;">
                        bilimon日志信息</div>
                    <div style="margin-left:15px"><i>🗒️此处展示bilimon程序的运行日志...</i></div>
                    <div
                        style="margin-left:15px;margin-right:15px;margin-top:10px;outline: 1px solid #3c3c3c;overflow:hidden">
                        <textarea cols="50" rows="32" wrap="off" readonly="readonly" id="log_content_bilimon"
                            autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false"
                            style="border:1px solid #000;width:99%; font-family:'Lucida Console'; font-size:11px;background:transparent;color:#FFFFFF;outline: none;padding-left:5px;padding-right:22px;line-height:1.3;overflow-x:hidden;white-space:break-spaces;"></textarea>
                    </div>
                    <div id="ok_button_bilimon" class="apply_gen" style="background:#000;">
                        <input class="button_gen" type="button" onclick="hide_log_pannel()" value="返回主界面">
                        <input style="margin-left:10px" type="checkbox" id="bilimon_stop_log">
                        <lable>&nbsp;暂停日志刷新</lable>
                    </div>
                </td>
            </tr>
        </table>
    </div>
    <table class="content" align="center" cellpadding="0" cellspacing="0">
        <tr>
            <td width="17">&nbsp;</td>
            <td valign="top" width="202">
                <div id="mainMenu"></div>
                <div id="subMenu"></div>
            </td>
            <td valign="top">
                <div id="tabMenu" class="submenuBlock"></div>
                <table width="98%" border="0" align="left" cellpadding="0" cellspacing="0">
                    <tr>
                        <td align="left" valign="top">
                            <table width="760px" border="0" cellpadding="5" cellspacing="0" bordercolor="#6b8fa3"
                                class="FormTitle" id="FormTitle">
                                <tr>
                                    <td bgcolor="#4D595D" colspan="3" valign="top">
                                        <div>&nbsp;</div>
                                        <div class="formfonttitle">BiliMon<lable id="bilimon_version">
                                                <lable>
                                        </div>
                                        <div style="float:right; width:15px; height:25px;margin-top:-20px">
                                            <img id="return_btn" onclick="reload_Soft_Center();" align="right"
                                                style="cursor:pointer;position:absolute;margin-left:-30px;margin-top:-25px;"
                                                title="返回软件中心" src="/images/backprev.png"
                                                onMouseOver="this.src='/images/backprevclick.png'"
                                                onMouseOut="this.src='/images/backprev.png'"></img>
                                        </div>
                                        <div style="margin:10px 0 10px 5px;" class="splitLine"></div>
                                        <div class="SimpleNote">
                                            <li>B站粉丝监控工具 BiliMon</li>
                                            <li style="color: #FC0;">请设置虚拟内存后再使用</li>
                                        </div>
                                        <div id="bilimon_main">
                                            <table width="100%" border="1" align="center" cellpadding="4"
                                                cellspacing="0" class="FormTable">
                                                <thead>
                                                    <tr>
                                                        <td colspan="2">BiliMon 设定</td>
                                                    </tr>
                                                </thead>
                                                <tr id="switch_tr">
                                                    <th>开关</th>
                                                    <td colspan="2">
                                                        <div class="switch_field"
                                                            style="display:table-cell;float: left;">
                                                            <label for="bilimon_enable">
                                                                <input id="bilimon_enable" class="switch"
                                                                    type="checkbox" style="display: none;">
                                                                <div class="switch_container">
                                                                    <div class="switch_bar"></div>
                                                                    <div class="switch_circle transition_style">
                                                                        <div></div>
                                                                    </div>
                                                                </div>
                                                            </label>
                                                        </div>
                                                        <div style="float: right;margin-top:5px;margin-right:5px;">
                                                            <a type="button" class="ks_btn" href="javascript:void(0);"
                                                                onclick="get_log(1)"
                                                                style="cursor: pointer;margin-left:5px;border:none">查看日志</a>
                                                        </div>
                                                    </td>
                                                </tr>
                                                <tr>
                                                    <th>运行状态</th>
                                                    <td><span id="bilimon_status"></span>
                                                        <div style="float: right;margin-right:5px;">
                                                            <a type="button" class="ks_btn" href="javascript:void(0);"
                                                                onclick="show_log_pannel()">BiliMon 运行日志</a>
                                                        </div>
                                                    </td>
                                                </tr>
                                                <tr>
                                                    <th>刷新周期(小时)<span style="color: red;"> * </span></th>
                                                    <td>
                                                        <input style="width:62px;" type="number" class="input_ss_table"
                                                            id="bilimon_feat_period" name="bilimon_feat_period" min="1"
                                                            max="8765" value="2">
                                                    </td>
                                                </tr>
                                                <tr>
                                                    <th>提示邮箱(QQ/Foxmail)<span style="color: red;"> * </span></th>
                                                    <td>
                                                        <input style="width:300px;" type="password"
                                                            class="input_ss_table" id="bilimon_feat_mail"
                                                            name="bilimon_feat_mail" maxlength="100" value=""
                                                            autocorrect="off" autocapitalize="off" readonly
                                                            onblur="switchType(this, false);"
                                                            onfocus="switchType(this, true);this.removeAttribute('readonly');"
                                                            value="">
                                                    </td>
                                                </tr>
                                                <tr>
                                                    <th>SMTP密钥<span style="color: red;"> * </span></th>
                                                    <td>
                                                        <input style="width:300px;" type="password"
                                                            class="input_ss_table" id="bilimon_feat_smtp"
                                                            name="bilimon_feat_smtp" maxlength="100" value=""
                                                            autocorrect="off" autocapitalize="off" readonly
                                                            onblur="switchType(this, false);"
                                                            onfocus="switchType(this, true);this.removeAttribute('readonly');"
                                                            value="">
                                                    </td>
                                                </tr>
                                                <tr>
                                                    <th>缓存路径<span style="color: red;"> * </span></th>
                                                    <td>
                                                        <input style="width:300px;" type="text" class="input_ss_table"
                                                            id="bilimon_feat_tmp" name="bilimon_feat_tmp"
                                                            maxlength="100" value="" autocorrect="off"
                                                            autocapitalize="off">
                                                    </td>
                                                </tr>
                                                <tr>
                                                    <th>B站Cookie</th>
                                                    <td>
                                                        <span id="cookie1">账号1<span style="color: red;"> *
                                                            </span></span>
                                                        <textarea style="width:453px;height:auto;"
                                                            class="input_ss_table" id="bilimon_feat_cookie"
                                                            name="bilimon_feat_cookie" maxlength="2048" rows="12"
                                                            autocorrect="off" autocapitalize="off"></textarea>
                                                        <span id="cookie2">账号2</span>
                                                        <textarea style="width:453px;height:auto;"
                                                            class="input_ss_table" id="bilimon_feat_cookie2"
                                                            name="bilimon_feat_cookie2" maxlength="2048" rows="12"
                                                            autocorrect="off" autocapitalize="off"></textarea>
                                                    </td>
                                                </tr>
                                                <tr id="bilimon_trigger">
                                                    <th>手动触发</th>
                                                    <td>
                                                        <a type="button" class="ks_btn bilimon_trigger"
                                                            href="javascript:void(0);" onclick="trigger(1)"
                                                            style="border:none">单轮粉丝扫描</a>
                                                        <a type="button" class="ks_btn bilimon_trigger"
                                                            href="javascript:void(0);" onclick="trigger(2)"
                                                            style="border:none">清理已注销狗</a>
                                                    </td>
                                                </tr>
                                                <tr id="bilimon_traitor">
                                                    <th>取关狗名单</th>
                                                    <td>
                                                        <a type="button" class="ks_btn bilimon_traitor"
                                                            href="javascript:void(0);" onclick="watchdog()"
                                                            style="border:none">取关狗名单</a>
                                                    </td>
                                                </tr>
                                                <tr id="bilimon_env">
                                                    <th>修复运行环境</th>
                                                    <td>
                                                        <a type="button" class="ks_btn bilimon_env"
                                                            href="javascript:void(0);" onclick="fixenv()"
                                                            style="border:none">修复运行环境</a>
                                                        <a type="button" class="ks_btn bilimon_trigger"
                                                            href="javascript:void(0);" onclick="trigger(3)"
                                                            style="border:none">SMTP测试</a>
                                                    </td>
                                                </tr>
                                            </table>
                                        </div>
                                        <div class="apply_gen">
                                            <input class="button_gen" id="bilimon_apply" onClick="save()" type="button"
                                                value="提交" />
                                        </div>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                </table>
            </td>
            <td width="10" align="center" valign="top"></td>
        </tr>
    </table>
    <div id="footer"></div>
</body>

</html>
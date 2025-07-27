<!DOCTYPE html
    PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">

<head>
    <meta http-equiv="X-UA-Compatible" content="IE=Edge" />
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <meta HTTP-EQUIV="Pragma" CONTENT="no-cache" />
    <meta HTTP-EQUIV="Expires" CONTENT="-1" />
    <link rel="shortcut icon" href="images/favicon.png" />
    <title>软件中心 - WeMediaMon</title>
    <link rel="stylesheet" type="text/css" href="index_style.css" />
    <link rel="stylesheet" type="text/css" href="form_style.css" />
    <link rel="stylesheet" type="text/css" href="css/element.css">
    <link rel="stylesheet" type="text/css" href="/res/softcenter.css">
    <link rel="stylesheet" type="text/css" href="/res/wemediamon.css">
    <link rel="stylesheet" type="text/css" href="/res/layer/theme/default/layer.css">
    <script language="JavaScript" type="text/javascript" src="/js/jquery.js"></script>
    <script type="text/javascript" src="/res/softcenter.js"></script>
    <script type="text/javascript" src="/state.js"></script>
    <script type="text/javascript" src="/general.js"></script>
    <script type="text/javascript" src="/popup.js"></script>
    <script type="text/javascript" src="/res/wemediamon.js"></script>
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
                        wemediamon日志信息</div>
                    <div style="margin-left:15px"><i>🗒️此处展示wemediamon程序的运行日志...</i></div>
                    <div
                        style="margin-left:15px;margin-right:15px;margin-top:10px;outline: 1px solid #3c3c3c;overflow:hidden">
                        <textarea cols="50" rows="32" wrap="off" readonly="readonly" id="log_content_wemediamon"
                            autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false"
                            style="border:1px solid #000;width:99%; font-family:'Lucida Console'; font-size:11px;background:transparent;color:#FFFFFF;outline: none;padding-left:5px;padding-right:22px;line-height:1.3;overflow-x:hidden;white-space:break-spaces;"></textarea>
                    </div>
                    <div id="ok_button_wemediamon" class="apply_gen" style="background:#000;">
                        <input class="button_gen" type="button" onclick="hide_log_pannel()" value="返回主界面">
                        <input style="margin-left:10px" type="checkbox" id="wemediamon_stop_log">
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
                                        <div class="formfonttitle">WeMediaMon<lable id="wemediamon_version">
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
                                            <li>自媒体粉丝监控工具 WeMediaMon</li>
                                            <li style="color: #FC0;">请设置虚拟内存后再使用</li>
                                        </div>
                                        <div id="wemediamon_main">
                                            <table width="100%" border="1" align="center" cellpadding="4"
                                                cellspacing="0" class="FormTable">
                                                <thead>
                                                    <tr>
                                                        <td colspan="2">WeMediaMon 设定</td>
                                                    </tr>
                                                </thead>
                                                <tr id="switch_tr">
                                                    <th>开关</th>
                                                    <td colspan="2">
                                                        <div class="switch_field"
                                                            style="display:table-cell;float: left;">
                                                            <label for="wemediamon_enable">
                                                                <input id="wemediamon_enable" class="switch"
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
                                                                onclick="get_log(1)" style="margin-left:5px">启动日志</a>
                                                            <a type="button" class="ks_btn wemediamon_env"
                                                                href="javascript:void(0);" onclick="fixenv()">环境修复</a>
                                                        </div>
                                                    </td>
                                                </tr>
                                                <tr>
                                                    <th>运行状态</th>
                                                    <td><span id="wemediamon_status"></span>
                                                        <div style="float: right;margin-right:5px;">
                                                            <a type="button" class="ks_btn" href="javascript:void(0);"
                                                                onclick="show_log_pannel()">运行日志</a>
                                                            <a type="button" class="ks_btn" href="javascript:void(0);"
                                                                onclick="show_log_pannel()">控制面板</a>
                                                        </div>
                                                    </td>
                                                </tr>
                                                <tr>
                                                    <th>提示邮箱(QQ/Foxmail)<span style="color: red;"> * </span></th>
                                                    <td>
                                                        <input style="width:300px;" type="password"
                                                            class="input_ss_table" id="wemediamon_feat_mail"
                                                            name="wemediamon_feat_mail" maxlength="100" value=""
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
                                                            class="input_ss_table" id="wemediamon_feat_smtp"
                                                            name="wemediamon_feat_smtp" maxlength="100" value=""
                                                            autocorrect="off" autocapitalize="off" readonly
                                                            onblur="switchType(this, false);"
                                                            onfocus="switchType(this, true);this.removeAttribute('readonly');"
                                                            value="">
                                                        <div style="float: right;margin-right:5px;">
                                                            <a type="button" class="ks_btn wemediamon_trigger"
                                                                href="javascript:void(0);" onclick="trigger(3)">邮件测试</a>
                                                        </div>
                                                    </td>
                                                </tr>
                                                <tr>
                                                    <th>缓存路径<span style="color: red;"> * </span></th>
                                                    <td>
                                                        <input style="width:300px;" type="text" class="input_ss_table"
                                                            id="wemediamon_feat_tmp" name="wemediamon_feat_tmp"
                                                            maxlength="100" value="" autocorrect="off"
                                                            autocapitalize="off">
                                                    </td>
                                                </tr>
                                                <tr id="wemediamon_period">
                                                    <th>刷新周期(小时)<span style="color: red;"> * </span></th>
                                                    <td>
                                                        <input style="width:62px;" type="number" class="input_ss_table"
                                                            id="wemediamon_feat_period" name="wemediamon_feat_period"
                                                            min="1" max="8765" value="2">
                                                    </td>
                                                </tr>
                                            </table>
                                        </div>
                                        <div id="tablets">
                                            <table style="margin:10px 0px 0px 0px;border-collapse:collapse" width="100%"
                                                height="37px">
                                                <tr>
                                                    <td cellpadding="0" cellspacing="0" style="padding:0" border="1"
                                                        bordercolor="#222">
                                                        <input onclick="tabSelect(0)" class="show show-btn0 active"
                                                            type="button" value="bilibili" />
                                                        <input onclick="tabSelect(1)" class="show show-btn1"
                                                            type="button" value="HuggingFace" />
                                                        <input onclick="tabSelect(2)" class="show show-btn2"
                                                            type="button" value="GitHub" />
                                                        <input onclick="tabSelect(3)" class="show show-btn3"
                                                            type="button" value="cnblogs" />
                                                        <input onclick="tabSelect(4)" class="show show-btn4"
                                                            type="button" value="itch.io" />
                                                    </td>
                                                </tr>
                                            </table>
                                        </div>
                                        <div id="tablet_0">
                                            <table id="table_0" width="100%" border="0" align="center" cellpadding="4"
                                                cellspacing="0" bordercolor="#6b8fa3" class="FormTable">
                                                <tr>
                                                    <th>BiliMon开关</th>
                                                    <td>
                                                        <input type="checkbox" id="check_0" onchange="show_hide_el(0)"
                                                            checked>
                                                    </td>
                                                </tr>
                                                <tr>
                                                    <th>B站Cookie<span style="color: red;"> * </span></th>
                                                    <td>
                                                        <textarea style="width:453px;height:auto;"
                                                            class="input_ss_table" id="bili_ck" name="bili_ck"
                                                            maxlength="2048" rows="12" autocorrect="off"
                                                            autocapitalize="off"
                                                            placeholder="浏览器-开发者工具-网络, 查看已登陆状态B站主页请求标头, 拷贝 Cookie 值至此"></textarea>
                                                    </td>
                                                </tr>
                                                <tr id="wemediamon_trigger">
                                                    <th>手动触发</th>
                                                    <td>
                                                        <a type="button" class="ks_btn wemediamon_trigger"
                                                            href="javascript:void(0);" onclick="">Cookie有效测试</a>
                                                        <a type="button" class="ks_btn wemediamon_trigger"
                                                            href="javascript:void(0);" onclick="trigger(1)">单轮粉丝扫描</a>
                                                    </td>
                                                </tr>
                                                <tr id="wemediamon_traitor">
                                                    <th>管理取关狗</th>
                                                    <td>
                                                        <a type="button" class="ks_btn wemediamon_traitor"
                                                            href="javascript:void(0);" onclick="watchdog()">查看取关狗名单</a>
                                                        <a type="button" class="ks_btn wemediamon_trigger"
                                                            href="javascript:void(0);" onclick="trigger(2)">清理已注销狗</a>
                                                    </td>
                                                </tr>
                                            </table>
                                        </div>
                                        <div id="tablet_1" style="display: none;">
                                            <table id="table_1" width="100%" border="0" align="center" cellpadding="4"
                                                cellspacing="0" bordercolor="#6b8fa3" class="FormTable">
                                                <tr>
                                                    <th>HFMon开关</th>
                                                    <td>
                                                        <input type="checkbox" id="check_1" onchange="show_hide_el(1)"
                                                            checked>
                                                    </td>
                                                </tr>
                                                <tr>
                                                    <th>监控目标<span style="color: red;"> * </span></th>
                                                    <td>
                                                        <input style="width:300px;" type="text" class="input_ss_table"
                                                            id="hf_tags" name="hf_tags" maxlength="100" value=""
                                                            autocorrect="off" autocapitalize="off"
                                                            placeholder="目前仅能填写一个用户名">
                                                    </td>
                                                </tr>
                                                <tr id="wemediamon_trigger">
                                                    <th>手动触发</th>
                                                    <td>
                                                        <a type="button" class="ks_btn wemediamon_trigger"
                                                            href="javascript:void(0);" onclick="trigger(1)">单轮粉丝扫描</a>
                                                        <a type="button" class="ks_btn wemediamon_trigger"
                                                            href="javascript:void(0);" onclick="trigger(1)">激活休眠仓库</a>
                                                    </td>
                                                </tr>
                                            </table>
                                        </div>
                                        <div id="tablet_2" style="display: none;">
                                            <table id="table_2" width="100%" border="0" align="center" cellpadding="4"
                                                cellspacing="0" bordercolor="#6b8fa3" class="FormTable">
                                                <tr>
                                                    <th>GitHubMon开关</th>
                                                    <td>
                                                        <input type="checkbox" id="check_2" onchange="show_hide_el(2)"
                                                            checked>
                                                    </td>
                                                </tr>
                                                <tr>
                                                    <th>监控目标<span style="color: red;"> * </span></th>
                                                    <td>
                                                        <input style="width:300px;" type="text" class="input_ss_table"
                                                            id="hf_tags" name="hf_tags" maxlength="100" value=""
                                                            autocorrect="off" autocapitalize="off"
                                                            placeholder="target1;target2;...">
                                                    </td>
                                                </tr>
                                                <tr id="wemediamon_trigger">
                                                    <th>手动触发</th>
                                                    <td>
                                                        <a type="button" class="ks_btn wemediamon_trigger"
                                                            href="javascript:void(0);" onclick="trigger(1)">单轮粉丝扫描</a>
                                                    </td>
                                                </tr>
                                            </table>
                                        </div>
                                        <div id="tablet_3" style="display: none;">
                                            <table id="table_basic" width="100%" border="0" align="center"
                                                cellpadding="4" cellspacing="0" bordercolor="#6b8fa3" class="FormTable">
                                            </table>
                                        </div>
                                        <div id="tablet_4" style="display: none;">
                                            <table id="table_basic" width="100%" border="0" align="center"
                                                cellpadding="4" cellspacing="0" bordercolor="#6b8fa3" class="FormTable">
                                            </table>
                                        </div>

                                        <div class="apply_gen">
                                            <input class="button_gen" id="wemediamon_apply" onClick="save()"
                                                type="button" value="提交" />
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
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
    <div id="LoadingBar" class="popup_bar_bg_ks">
        <table cellpadding="5" cellspacing="0" id="loadingBarBlock" class="loadingBarBlock" align="center">
            <tr>
                <td height="100">
                    <div id="loading_block_title"></div>
                    <div id="loading_block_spilt" class="loading_block_spilt"></div>
                    <div id="log_container">
                        <textarea cols="50" rows="25" wrap="soft" readonly="readonly" id="run_log_content"
                            autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false"></textarea>
                    </div>
                    <div id="ok_button" class="apply_gen">
                        <input id="ok_btn" class="button_gen" type="button" onclick="hideWBLoadingBar()" value="确定">
                    </div>
                </td>
            </tr>
        </table>
    </div>
    <div id="log_pannel_div" class="popup_bar_bg_ks">
        <table cellpadding="5" cellspacing="0" id="log_pannel_table" class="loadingBarBlock" align="center">
            <tr>
                <td height="100">
                    <div id="log_info">wemediamon监控信息</div>
                    <div style="margin-left:15px">🗒️<i id="log_pannel_title">此处展示wemediamon程序的监控日志...</i></div>
                    <div id="running_log">
                        <textarea cols="50" rows="32" wrap="soft" readonly="readonly" id="log_content"
                            autocomplete="off" autocorrect="off" autocapitalize="off" spellcheck="false"></textarea>
                    </div>
                    <div id="mon_ok_button" class="apply_gen">
                        <input class="button_gen" type="button" onclick="hide_log_pannel()" value="返回主界面">
                        <input type="checkbox" class="stop_log">
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
                                        <div id="return_center">
                                            <img id="return_btn" onclick="reload_Soft_Center();" align="right"
                                                title="返回软件中心" src="/images/backprev.png"
                                                onMouseOver="this.src='/images/backprevclick.png'"
                                                onMouseOut="this.src='/images/backprev.png'">
                                        </div>
                                        <div class="splitLine"></div>
                                        <div class="SimpleNote">
                                            <li>自媒体监控工具 WeMediaMon</li>
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
                                                        <div class="switch_field">
                                                            <label for="enable">
                                                                <input id="enable" class="switch" type="checkbox">
                                                                <div class="switch_container">
                                                                    <div class="switch_bar"></div>
                                                                    <div class="switch_circle transition_style">
                                                                        <div></div>
                                                                    </div>
                                                                </div>
                                                            </label>
                                                        </div>
                                                        <div id="switch_btn">
                                                            <a type="button" class="ks_btn" href="javascript:void(0);"
                                                                onclick="show_mon_log()"
                                                                style="margin-left:5px">监控日志</a>
                                                        </div>
                                                    </td>
                                                </tr>
                                                <tr>
                                                    <th>运行状态</th>
                                                    <td><span id="status"></span>
                                                        <div id="status_container">
                                                            <a type="button" class="ks_btn" href="javascript:void(0);"
                                                                onclick="get_run_log(1)">执行日志</a>
                                                        </div>
                                                    </td>
                                                </tr>
                                                <tr>
                                                    <th>提示邮箱(QQ/Foxmail)<span style="color: red;"> * </span></th>
                                                    <td>
                                                        <input type="text" class="input_ss_table" id="email"
                                                            maxlength="100" value="" autocorrect="off"
                                                            autocapitalize="off">
                                                    </td>
                                                </tr>
                                                <tr>
                                                    <th>SMTP密钥<span style="color: red;"> * </span></th>
                                                    <td>
                                                        <input type="password" class="input_ss_table" id="smtp"
                                                            maxlength="100" value="" autocorrect="off"
                                                            autocapitalize="off" readonly
                                                            onblur="switchType(this, false);"
                                                            onfocus="switchType(this, true);this.removeAttribute('readonly');"
                                                            value="">
                                                        <div class="right_btn">
                                                            <a type="button" class="ks_btn" href="javascript:void(0);"
                                                                onclick="trigger('TEST_SMTP')">邮件测试</a>
                                                        </div>
                                                    </td>
                                                </tr>
                                                <tr>
                                                    <th>缓存路径<span style="color: red;"> * </span></th>
                                                    <td>
                                                        <input type="text" class="input_ss_table" id="cache"
                                                            maxlength="100" value="" autocorrect="off"
                                                            autocapitalize="off">
                                                        <div class="right_btn">
                                                            <a type="button" class="ks_btn" href="javascript:void(0);"
                                                                onclick="trigger('FIX_ENV')">环境修复</a>
                                                        </div>
                                                    </td>
                                                </tr>
                                                <tr>
                                                    <th>刷新周期(小时)<span style="color: red;"> * </span></th>
                                                    <td>
                                                        <input type="number" class="input_ss_table" id="period" min="1"
                                                            max="8765" value="2">
                                                    </td>
                                                </tr>
                                                <tr>
                                                    <th>导入配置</th>
                                                    <td>
                                                        <input type="file" class="input_ss_table" id="config"
                                                            accept=".json">
                                                        <div class="right_btn">
                                                            <a type="button" class="ks_btn" href="javascript:void(0);"
                                                                onclick="export_cfg()">导出配置</a>
                                                        </div>
                                                    </td>
                                                </tr>
                                            </table>
                                        </div>
                                        <div id="tablets">
                                            <table width="100%" height="37px">
                                                <tr>
                                                    <td cellpadding="0" cellspacing="0" border="1" bordercolor="#222">
                                                        <input onclick="tabSelect(0)" class="show-btn0 active"
                                                            type="button" value="bilibili" />
                                                        <input onclick="tabSelect(1)" class="show-btn1" type="button"
                                                            value="HuggingFace" />
                                                        <input onclick="tabSelect(2)" class="show-btn2" type="button"
                                                            value="GitHub" />
                                                        <input onclick="tabSelect(3)" class="show-btn3" type="button"
                                                            value="cnblogs" />
                                                        <input onclick="tabSelect(4)" class="show-btn4" type="button"
                                                            value="itch.io" />
                                                    </td>
                                                </tr>
                                            </table>
                                        </div>
                                        <div id="tablet_0">
                                            <table id="table_0" width="100%" border="0" align="center" cellpadding="4"
                                                cellspacing="0" bordercolor="#6b8fa3" class="FormTable">
                                                <tr>
                                                    <th>B站监控开关</th>
                                                    <td>
                                                        <input type="checkbox" class="check_0" id="bilimon"
                                                            onchange="show_hide(0)">
                                                    </td>
                                                </tr>
                                                <tr>
                                                    <th>B站Cookie<span style="color: red;"> * </span></th>
                                                    <td>
                                                        <textarea class="input_ss_table" id="bilick" maxlength="2048"
                                                            rows="12" autocorrect="off" autocapitalize="off"
                                                            placeholder="浏览器-开发者工具-网络, 查看已登陆状态B站主页请求标头, 拷贝 Cookie 值至此"></textarea>
                                                    </td>
                                                </tr>
                                                <tr>
                                                    <th>每日自动签到</th>
                                                    <td>
                                                        <input type="password" class="input_ss_table" id="btskon"
                                                            maxlength="32" value="" autocorrect="off"
                                                            autocapitalize="off" readonly
                                                            onblur="switchType(this, false);"
                                                            onfocus="switchType(this, true);this.removeAttribute('readonly');"
                                                            placeholder="留空则不开启, 浏览器控制台输入window.localStorage.ac_time_value访问B站主页获取">
                                                        <input type="time" class="input_ss_table" id="btskat"
                                                            value="00:01">
                                                    </td>
                                                </tr>
                                                <tr>
                                                    <th>手动触发</th>
                                                    <td>
                                                        <a type="button" class="ks_btn" href="javascript:void(0);"
                                                            onclick="trigger('TEST_BILI_CK')">Cookie有效测试</a>
                                                        <a type="button" class="ks_btn" href="javascript:void(0);"
                                                            onclick="trigger('UPD_BILI_FANS')">单轮粉丝扫描</a>
                                                        <a type="button" class="ks_btn" href="javascript:void(0);"
                                                            onclick="trigger('TEST_BILI_TASKS')">测试一键签到</a>
                                                    </td>
                                                </tr>
                                                <tr>
                                                    <th>管理取关狗</th>
                                                    <td>
                                                        <a type="button" class="ks_btn" href="javascript:void(0);"
                                                            onclick="trigger('SEE_BILI_BLACKS')">查看取关狗名单</a>
                                                        <a type="button" class="ks_btn" href="javascript:void(0);"
                                                            onclick="trigger('UPD_BILI_BLACKS')">清理已注销狗</a>
                                                    </td>
                                                </tr>
                                            </table>
                                        </div>
                                        <div id="tablet_1" style="display: none;">
                                            <table id="table_1" width="100%" border="0" align="center" cellpadding="4"
                                                cellspacing="0" bordercolor="#6b8fa3" class="FormTable">
                                                <tr>
                                                    <th>抱脸监控开关</th>
                                                    <td>
                                                        <input type="checkbox" class="check_1" id="hfmon"
                                                            onchange="show_hide(1)">
                                                    </td>
                                                </tr>
                                                <tr>
                                                    <th>Token(s)<span style="color: red;"> * </span></th>
                                                    <td>
                                                        <input type="password" class="input_ss_table" id="hftks"
                                                            maxlength="100" value="" autocorrect="off"
                                                            autocapitalize="off" readonly
                                                            onblur="switchType(this, false);"
                                                            onfocus="switchType(this, true);this.removeAttribute('readonly');"
                                                            placeholder="若多个则用;隔开">
                                                    </td>
                                                </tr>
                                                <tr>
                                                    <th>监控论文<span style="color: red;"> * </span></th>
                                                    <td>
                                                        <input type="text" class="input_ss_table" id="papers"
                                                            maxlength="100" value="" autocorrect="off"
                                                            autocapitalize="off" placeholder="若多个则用;隔开">
                                                    </td>
                                                </tr>
                                                <tr>
                                                    <th>手动触发</th>
                                                    <td>
                                                        <a type="button" class="ks_btn" href="javascript:void(0);"
                                                            onclick="trigger('UPD_HF_FANS')">单轮粉丝扫描</a>
                                                        <a type="button" class="ks_btn" href="javascript:void(0);"
                                                            onclick="trigger('ACTIVATE_HF_REPOS')">单轮激活空间</a>
                                                    </td>
                                                </tr>
                                                <tr>
                                                    <th>管理取关狗</th>
                                                    <td>
                                                        <a type="button" class="ks_btn" href="javascript:void(0);"
                                                            onclick="trigger('SEE_HF_BLACKS')">查看取关狗名单</a>
                                                        <a type="button" class="ks_btn" href="javascript:void(0);"
                                                            onclick="trigger('UPD_HF_BLACKS')">清理已注销狗</a>
                                                    </td>
                                                </tr>
                                            </table>
                                        </div>
                                        <div id="tablet_2" style="display: none;">
                                            <table id="table_2" width="100%" border="0" align="center" cellpadding="4"
                                                cellspacing="0" bordercolor="#6b8fa3" class="FormTable">
                                                <tr>
                                                    <th>GitHub监控开关</th>
                                                    <td>
                                                        <input type="checkbox" class="check_2" id="gitmon"
                                                            onchange="show_hide(2)">
                                                    </td>
                                                </tr>
                                                <tr>
                                                    <th>监控目标<span style="color: red;"> * </span></th>
                                                    <td>
                                                        <input type="text" class="input_ss_table" id="gitags"
                                                            maxlength="100" value="" autocorrect="off"
                                                            autocapitalize="off" placeholder="target1;target2;...">
                                                    </td>
                                                </tr>
                                                <tr>
                                                    <th>手动触发</th>
                                                    <td>
                                                        <a type="button" class="ks_btn" href="javascript:void(0);"
                                                            onclick="trigger('UPD_GIT_FANS')">单轮粉丝扫描</a>
                                                    </td>
                                                </tr>
                                                <tr>
                                                    <th>管理取关狗</th>
                                                    <td>
                                                        <a type="button" class="ks_btn" href="javascript:void(0);"
                                                            onclick="trigger('SEE_GIT_BLACKS')">查看取关狗名单</a>
                                                        <a type="button" class="ks_btn" href="javascript:void(0);"
                                                            onclick="trigger('UPD_GIT_BLACKS')">清理已注销狗</a>
                                                    </td>
                                                </tr>
                                            </table>
                                        </div>
                                        <div id="tablet_3" style="display: none;">
                                            <table id="table_3" width="100%" border="0" align="center" cellpadding="4"
                                                cellspacing="0" bordercolor="#6b8fa3" class="FormTable">
                                                <tr>
                                                    <th>博客园监控开关</th>
                                                    <td>
                                                        <input type="checkbox" class="check_3" id="cnblon"
                                                            onchange="show_hide(3)">
                                                    </td>
                                                </tr>
                                                <tr>
                                                    <th>博客园Cookie<span style="color: red;"> * </span></th>
                                                    <td>
                                                        <textarea class="input_ss_table" id="cnblokie" maxlength="2048"
                                                            rows="12" autocorrect="off" autocapitalize="off"
                                                            placeholder="浏览器-开发者工具-网络, 查看已登陆状态博客园主页请求标头, 拷贝 Cookie 值至此"></textarea>
                                                    </td>
                                                </tr>
                                                <tr>
                                                    <th>手动触发</th>
                                                    <td>
                                                        <a type="button" class="ks_btn" href="javascript:void(0);"
                                                            onclick="trigger('TEST_CNBLOGS_CK')">Cookie有效测试</a>
                                                        <a type="button" class="ks_btn" href="javascript:void(0);"
                                                            onclick="trigger('UPD_CNBLOGS_FANS')">单轮粉丝扫描</a>
                                                    </td>
                                                </tr>
                                                <tr>
                                                    <th>管理取关狗</th>
                                                    <td>
                                                        <a type="button" class="ks_btn" href="javascript:void(0);"
                                                            onclick="trigger('SEE_CNBLOGS_BLACKS')">查看取关狗名单</a>
                                                        <a type="button" class="ks_btn" href="javascript:void(0);"
                                                            onclick="trigger('UPD_CNBLOGS_BLACKS')">清理已注销狗</a>
                                                    </td>
                                                </tr>
                                            </table>
                                        </div>
                                        <div id="tablet_4" style="display: none;">
                                            <table id="table_4" width="100%" border="0" align="center" cellpadding="4"
                                                cellspacing="0" bordercolor="#6b8fa3" class="FormTable">
                                                <tr>
                                                    <th>itch.io监控开关</th>
                                                    <td>
                                                        <input type="checkbox" class="check_4" id="itchion"
                                                            onchange="show_hide(4)">
                                                    </td>
                                                </tr>
                                                <tr>
                                                    <th>itch.io cookie<span style="color: red;"> * </span></th>
                                                    <td>
                                                        <textarea class="input_ss_table" id="itck" maxlength="2048"
                                                            rows="12" autocorrect="off" autocapitalize="off"
                                                            placeholder="浏览器-开发者工具-网络, 查看已登陆状态itch.io主页请求标头, 拷贝 Cookie 值至此"></textarea>
                                                    </td>
                                                </tr>
                                                <tr>
                                                    <th>手动触发</th>
                                                    <td>
                                                        <a type="button" class="ks_btn" href="javascript:void(0);"
                                                            onclick="trigger('TEST_ITCH_CK')">Cookie有效测试</a>
                                                        <a type="button" class="ks_btn" href="javascript:void(0);"
                                                            onclick="trigger('UPD_ITCH_FANS')">单轮粉丝扫描</a>
                                                    </td>
                                                </tr>
                                                <tr>
                                                    <th>管理取关狗</th>
                                                    <td>
                                                        <a type="button" class="ks_btn" href="javascript:void(0);"
                                                            onclick="trigger('SEE_ITCH_BLACKS')">查看取关狗名单</a>
                                                        <a type="button" class="ks_btn" href="javascript:void(0);"
                                                            onclick="trigger('UPD_ITCH_BLACKS')">清理已注销狗</a>
                                                    </td>
                                                </tr>
                                            </table>
                                        </div>

                                        <div class="apply_gen">
                                            <input class="button_gen" id="apply" onclick="trigger('WEB_SUBMIT')"
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
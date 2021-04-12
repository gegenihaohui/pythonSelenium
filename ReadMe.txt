
【 用 例 编 写 注 意 事 项 】
1.在'Project'下创建'项目名称'目录：Project > pro_demo_1
2.在'项目名称'目录下创建两个目录：page_object、test_case
3.在'page_object'目录下提供：元素定位、页面操作方法
4.在'case_test'目录下提供：测试用例
5.在'Config > pro_config.py'文件中进行项目配置：
（1）get_test_class_list：通过'项目名'获取'测试类'列表
（2）pro_exist：判断项目名称是否存在
（3）get_login_accout：通过线程名的索引 获取登录账号
    < 注意：开启的线程数量，不能超过设置的账号数量 >



########################################################################################################################


【 本 地 配 置 项 目 开 发 环 境 】

1.配置本地 venv 虚拟环境
（1）修改：requirements_init.txt
（2）删除：原有 venv 目录
（3）执行：sh -x venv_install.sh

2.配置 gulpfile 依赖
（1）修改：gulpfile_install.sh
（2）删除：原有的 package.json 文件
（3）执行：sh -x gulpfile_install.sh

3.配置 Nginx -> python_selenium.conf

upstream api_server_WEB{
  server 127.0.0.1:8081 weight=1 max_fails=2 fail_timeout=30s;
  ip_hash;
}

server {
  listen 8070;
  server_name localhost;

  location /test_report_local/ {
        sendfile off;
        expires off;
        gzip on;
        gzip_min_length 1000;
        gzip_buffers 4 8k;
        gzip_types application/json application/javascript application/x-javascript text/css application/xml;
        add_header Cache-Control no-cache;
        add_header Cache-Control 'no-store';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header REMOTE-HOST $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_next_upstream error timeout invalid_header http_500 http_502 http_503 http_504;
        alias /Users/micllo/Documents/works/GitHub/pythonSelenium/Reports/;
       }

  location /api_local/ {
         proxy_set_header Host $host;
         proxy_set_header X-Real-IP $remote_addr;
         proxy_set_header REMOTE-HOST $remote_addr;
         proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
         proxy_next_upstream error timeout invalid_header http_500 http_502 http_503 http_504 http_404;
         proxy_pass http://api_server_WEB/;
         #proxy_pass http://127.0.0.1:8081/;
         proxy_redirect default;
  }
}

【 备 注 】
MAC本地安装的 nginx 相关路径
默认安装路径：/usr/local/Cellar/nginx/1.15.5/
默认配置文件路径：/usr/local/etc/nginx/
sudo nginx
sudo nginx -t
sudo nginx -s reload

/Users/micllo/nginx_logs/access.log

/Users/micllo/nginx_logs/error.log

########################################################################################################################


【 本地 Mac 相关 】

1.uWSGI配置文件：./vassals_local/app_uwsgi_local.ini
（1）启动 uWSGI 命令 在 ./start_uwsgi_local.sh 脚本
（2）停止 uWSGI 命令 在 ./stop_uwsgi_local.sh 脚本

2.上传 GitHub 需要被忽略的文件
（1）Logs、Reports、Screenshot -> 临时生产的 日志、报告、截图
（2）vassals_local、venv -> 本地的 uWSGI配置、python3虚拟环境
（3）node_modules、gulpfile.js、package.json、package-lock.json -> 供本地启动使用的gulp工具

3.访问地址（ server.py 启动 ）：
（1）接口地址 -> http://127.0.0.1:8082/
               http://127.0.0.1:8082/WEB/sync_run_case
               http://127.0.0.1:8082/WEB/get_img/5e5cac9188121299450740b3

4.访问地址（ uwsgi 启动 ）：
（1）用例页面 -> http://localhost:8070/api_local/WEB/index
（2）测试报告 -> http://127.0.0.1:8070/test_report_local/<pro_name>/[WEB_report]<pro_name>.html
（3）接口地址 -> http://127.0.0.1:8070/api_local/
               http://127.0.0.1:8070/api_local/WEB/sync_run_case
               http://127.0.0.1:8070/api_local/WEB/get_img/5e5cac9188121299450740b3
   （ 备注：uwgsi 启动 8081 端口、nginx 配置 8070 反向代理 8081 ）

5.本地相关服务的启动操作（ gulpfile.js 文件 ）
（1）启动服务并调试页面：gulp "html debug"
（2）停止服务命令：gulp "stop env"
（3）部署docker服务：gulp "deploy docker"

6.添加依赖：
pip3 install -v flask==0.12 -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com


########################################################################################################################


【 Docker Centos7 相关 】

1.uWSGI配置文件：vassals_docker/app_uwsgi.ini
（1）启动 uWSGI 命令 在 ./start_uwsgi.sh 脚本
（2）停止 uWSGI 命令 在 ./stop_uwsgi.sh 脚本

2.服务器目录结构
  /var/log/uwsgi/ 		   -> pid_uwsgi.pid、app_uwsgi.log、emperor.log
  /var/log/nginx/ 		   -> error.log、access.log
  /etc/uwsgi/vassals/	   -> app_uwsgi.ini
  /opt/project/logs/ 	   -> 项目日志
  /opt/project/reports/	   -> 测试报告
  /opt/project/${pro_name} -> 项目
  /opt/project/tmp         -> 临时目录(部署时使用)

3.服务器部署命令：
（1）从GitGub上拉取代码至临时目录
（2）关闭nginx、mongo、uwsgi服务
（3）替换项目、uwsgi.ini配置文件
（4）替换env_config配置文件
（5）启动nginx、mongo、uwsgi服务
（6）清空临时文件

4.部署时的存放位置：
（1）./pythonSelenium -> /opt/project/pythonSelenium
（2）./pythonSelenium/vassals/app_uwsgi.ini -> /etc/uwsgi/vassals/app_uwsgi.ini

5.部署时相关配置文件的替换操作：
（1）将./Env/目录下的 env_config.py 删除
（2）将./Env/目录下的 env_config_docker.py 重命名为 env_config.py

6.访问地址（ Docker 内部 ）：
（1）测试报告 -> http://127.0.0.1:80/test_report/<pro_name>/[WEB_report]<pro_name>.html
（2）接口地址 -> http://127.0.0.1:80/api/
               http://127.0.0.1:80/api/WEB/sync_run_case
               http://127.0.0.1:80/api/WEB/get_img/5e5cac9188121299450740b3
    ( 备注：uwgsi 启动 8081 端口、nginx 配置 80 反向代理 8081 )

7.访问地址（ 外部访问 ）：
（1）用例页面 -> http://192.168.31.9:1080/api/WEB/index
（2）测试报告 -> http://192.168.31.9:1080/test_report/<pro_name>/[WEB_report]<pro_name>.html
（3）接口地址 -> http://192.168.31.9:1080/api/
               http://192.168.31.9:1080/api/WEB/sync_run_case
               http://192.168.31.9:1080/api/WEB/get_img/5e5cac9188121299450740b3
    ( 备注：docker 配置 1080 映射 80 )

8.关于部署
  方式一：通过'shell'脚本命令进行部署
         sh /Users/micllo/Documents/works/expect-deploy/docker_python/deploy.sh pythonSelenium 127.0.0.1 1022
  方式二：通过'fabric'工具进行部署 -> deploy.py
    （1）将本地代码拷贝入临时文件夹，并删除不需要的文件目录
    （2）将临时文件夹中的该项目压缩打包，上传至服务器的临时文件夹中
    （3）在服务器中进行部署操作：停止nginx、mongo、uwsgi服务 -> 替换项目、uwsgi.ini配置文件 -> 替换config配置文件 -> 启动nginx、mongo、uwsgi服务
    （4）删除本地的临时文件夹
  方式三：通过'gulp'命令 执行 deploy.py 文件 进行部署


9.关于 Selenium Grid Console
（1）Hub 界面地址
    http://localhost:5555/grid/console
    http://192.168.31.10:5555/grid/console
（2）使用mac自带的远程桌面工具进入debug模式的界面
    在Finder图标右键选择'连接服务器' -> vnc://127.0.0.1:5911 -> 默认密码：secret



########################################################################################################################

【 框 架 工 具 】
 Python3 + Selenium3 + unittest + Flask + uWSGI + Nginx + Bootstrap + MongoDB + Docker + Fabric + Gulp


【 框 架 结 构 】（ 提高代码的：可读性、重用性、易扩展性 ）
 1.Api层：       对外接口、原静态文件
 2.Build层：     编译后的静态文件
 3.Common层：    通用方法、测试方法
 4.Config层：    错误码映射、全局变量、定时任务、项目配置、测试地址配置
 5.Data层：      相关测试数据
 6.Env层：       环境配置
 7.Project层：   区分不同项目、page_object(页面操作方法、元素定位)、test_case(测试用例)
 8.TestBase层：  封装了浏览器驱动操作方法、提供'测试用例'父类的基础方法(继承’unittest.TestCase')、测试报告生成、同步执行用例方法
 9.Tools层：     工具函数
 10.其他：
 （1）vassals/ -> 服务器的'uWSGI配置'
 （2）vassals_local/、venv/ -> 本地的'uWSGI配置、python3虚拟环境'
 （3）Logs/、Reports/、Screenshot/ -> 临时生产的 日志、报告、截图
 （4）node_modules/、gulpfile.js、package.json、package-lock.json -> 供本地启动使用的gulp工具
 （5）deploy.py、start_uwsgi_local.sh、stop_uwsgi_local.sh、tmp_uwsgi_pid.txt -> 本地部署文件及相关命令和临时文件

【 功 能 点 】

1.使用 Python3 + Selenium3 + unittest + Bootstrap:
（1）使用'unittest'作为测试用例框架
（2）通过动态修改和添加'unittest.TestSuite'类中的方法和属性，实现启用多线程同时执行多条测试用例
（3）通过修改'HTMLTestRunner'文件并结合'unittest'测试框架，优化了测试报告的展示方式，并提供了每个测试用例的截图显示
（4）所有用例执行后，若有'失败'或'错误'的用例，则发送钉钉和邮件通知
（5）提供日志记录功能：按照日期区分
（6）提供定时任务：定时删除过期(一周前)的文件：日志、报告、截图文件(mongo数据)，定时执行测试用例
（7）提供页面展示项目用例，实现用例上下线、批量执行用例、显示报告、用例运行进度等功能

2.使用 Flask ：
（1）提供 执行用例的接口
（2）提供 获取截图的接口：供测试报告页面调用

3.使用 Nginx ：
（1）提供测试报告的查看地址
（2）反向代理相关接口、解决测试报告调用'获取截图接口'时的跨域访问问题

4.使用 uWSGI :
（1）用作 web 服务器
（2）使用'emperor'命令进行管理：监视和批量启停 vassals 目录下 uwsgi 相关的 .ini 文件

5.使用 Docker：
（1）使用Dockerfile构建centos7镜像：提供项目所需的相关配置环境
（2）使用'selenium/hub'和'selenium/node-chrome-debug'镜像，搭建'Selenium Grid'分布式测试环境
     （ 可以在linux中启动无界面浏览器测试，并可以指定浏览器的分辨率和实例个数，可以通过'VNC'连接进行调试）
（3）使用'docker-compose' 一键管理多个容器

6.使用 MongoDB ：
（1）使用'GridFS'进行图片文件的保存与读取

7.使用 Fabric ：
（1）配置相关脚本，实现一键部署

8.使用 NodeJS 的 Gulp 命令 ：
（1）配置本地启动的相关服务，实现一键启动或停止
（2）编译静态文件，防止浏览器缓存js问题
（3）实时监听本地调试页面功能



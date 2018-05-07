# harbor开发用脚手架
## 1、快速使用
### 1.1、初始化项目
#### 1.1.1 清除旧有文件
<pre><code>python clear.py</code></pre>

#### 1.1.2 修改目录下harbor.yaml
<pre><code>anglers:
  - ../dockers/blog
  - ../dockers/frame
</code></pre>
配置引入调试的项目，anglers节点为数组格式，其中配置引入的项目路径
#### 1.1.3、运行同步程序
<pre><code>python sync.py</code></pre>
程序将会将代码同步进当前目录中。其中包含config中的配置文件、filiters过滤器、resources中的资源程序，以及services服务。
#### 1.1.4、修改各部分配置文件
将config中的各部分配置文件，修改为调试程序时所需要的程序。

其中config\angler\config.yaml中的内容为各模块合并结果，修改成需要的对应结果。

其中config\log\logging.conf为各模块合并内容，修改成需要的对应结果。

#### 1.1.5、修改服务需要修改的内容
services目录下的__init__.py文件为程序代码合并而成，修改对应的内容


### 1.2、运行项目：
<pre><code>python dev.py</code></pre>

## 2、各部分合并规则
### 2.1 config配置合并
#### 2.1.1 config/angler/config.yaml配置

#### 2.1.2 config/log/logging.conf配置

### 2.2 filiters合并

### 2.3 resources合并
将配置中的项目中的resources中的内容，此处仍然按照项目目录进行存放。此处与service


### 2.4 services合并
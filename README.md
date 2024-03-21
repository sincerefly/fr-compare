# fr-compare

封装 [face_recognition](https://github.com/ageitgey/face_recognition) 制作成Docker，提供裁剪人像与人像比对相似度两个接口

## Quick Start

安装依赖前确认本机环境已安装 gcc，设置环境变量参考: [README_Simplified_Chinese.md](https://github.com/ageitgey/face_recognition/blob/master/README_Simplified_Chinese.md)

```bash
# 安装依赖
$ pipenv --python 3.12
$ pipenv shell
$ pipenv install

# 运行
$ python3 fr-compare-2.0.py
* Detect or Compare with Fr_py, Server 2.0
* Running on http://0.0.0.0:8726/detect
* Running on http://0.0.0.0:8726/compare (Press CTRL+C to quit)
```

## Usage

```bash
# 构建镜像
$ sudo docker build -t fr-compare:2.0.0 .

# 启动容器
$ sudo docker run --restart=always --name fr-compare -d -p 8726:8726 fr-compare:2.0.0
```

访问http://[your-server-ip]:8726, 页面输出

```
{"code":200,"message":"face_recognition server 2.0"}
```

### 裁剪

http://[your-server-ip]:8726/detect （POST）

请求头

```
'Content-Type': 'application/json'
```

请求体

```
{
    "b64_image": "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAIBAQEBAQIBAQEC..."
}
```

回复内容

```
{
    "b64_image": "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAIBAQEBAQIBAQEC...", "message": "success"
}
```

返回的 b64_image 为裁剪后的头像数据, message 为 "succcess" 时为截取头像成功, 否则为报错信息并且b64_image 为空字符串


### 比对

http://[your-server-ip]:8722/detect （POST）

请求头

```
'Content-Type': 'application/json'
```

请求体

```
{
    "b64_image_01": "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAIBAQEBAQIBAQEC..."，
    "b64_image_02": "/9j/4AAQSkZJRgABAQAAAQABAAD/2wBDAAIBAQEBAQIBAQEC..."
}
```

回复内容

```
{
    "message": "ok",
    "distance": 56.84
}
```

distance 值越高，两张照片为一个人的概率越大


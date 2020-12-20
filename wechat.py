
from flask import Flask, request, abort, render_template
import hashlib, xmltodict, time, urllib.request, json

# 常量
# 微信的token令牌
WECHAT_TOKEN = "itcast"
WECHAT_APPID = "wxbb8a530a254f3aa8"
WECHAT_SECRET = "9852daebdbb4d648e570544ab104d194"

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def wechat():
    """对接微信公众号服务器"""
    signature = request.args.get("signature")
    timestamp = request.args.get("timestamp")
    nonce = request.args.get("nonce")
    #

    # 效验参数
    if not all([signature, timestamp, nonce]):
        abort(400)

    # 按照微信的流程进行计算签名
    li = [WECHAT_TOKEN, timestamp, nonce]
    # 排序
    li.sort()
    # 拼接字符串
    temp_str = "".join(li)
    # 进行sha1加密, 得到正确的签名值
    sign = hashlib.sha1(temp_str.encode()).hexdigest()

    # 将自己计算的签名值与请求的签名参数进行对比,如果相同,则证明请求来自微信服务器
    if signature != sign:
        # 表示请求不是微信发的
        abort(403)
    else:
        # 表示是微信发送的请求
        if request.method == "GET":
            # 表示是第一次接入微信服务器的验证
            echostr = request.args.get("echostr")
            if not echostr:
                abort(400)
            return echostr
        elif request.method == "POST":
            # 表示微信服务器转发消息过来
            xml_str = request.data
            if not xml_str:
                abort(400)
            # 对xml字符串进行解析
            xml_dict = xmltodict.parse(xml_str).get("xml")

            # 提取消息类型
            msgType = xml_dict.get("MsgType")
            if msgType == "text":
                # 表示发送的是文本消息
                # 构造返回值, 经由微信服务器回复给用户的消息内容
                text = xml_dict.get("Content")
                if text == "网址":
                    text = '''https://open.weixin.qq.com/connect/oauth2/authorize?appid=wxbb8a530a254f3aa8&redirect_uri=http://3v5s579241.wicp.vip/index&response_type=code&scope=snsapi_userinfo&state=STATE#wechat_redirect'''
                resp_dict = {
                    "xml":{
                        "ToUserName": xml_dict.get("FromUserName"),
                        "FromUserName": xml_dict.get("ToUserName"),
                        "CreateTime": int(time.time()),
                        "MsgType": "text",
                        "Content": text
                    }
                }
            else:
                resp_dict = {
                    "xml": {
                        "ToUserName": xml_dict.get("FromUserName"),
                        "FromUserName": xml_dict.get("ToUserName"),
                        "CreateTime": int(time.time()),
                        "MsgType": "text",
                        "Content": "i love u"
                    }
                }
            # 将字典转换为xml字符串
            resp_xml_str = xmltodict.unparse(resp_dict)
            # 返回消息数据给微信服务器
            return resp_xml_str

@app.route("/index")
def index():
    """让用户通过微信访问的网页页面视图"""
    # 从微信服务器中拿去用户的资料数据
    # 1. 拿取code参数
    code = request.args.get("code")

    if not code:
        return u"缺失code参数"

    # 2. 想微信服务器发送http请求, 获取access_token
    url = "https://api.weixin.qq.com/sns/oauth2/access_token?appid=%s&secret=%s&code=%s&grant_type=authorization_code"\
        % (WECHAT_APPID, WECHAT_SECRET, code)

    # 使用urlopen方法发送请求
    # 如果只传网址url参数, 则默认使用http的get请求方式, 返回响应对象
    response = urllib.request.urlopen(url)

    # 获取响应体数据, 微信返回响应体数据
    json_str = response.read()
    resp_dict = json.loads(json_str)

    # 提取access_token
    if "errcode" in resp_dict:
        return u"获取access_token失败"

    access_token = resp_dict.get("access_token")
    open_id = resp_dict.get("openid") # 用户的编号

    # 3. 向微信服务器发送http请求, 获取用户资料数据
    url = "https://api.weixin.qq.com/sns/userinfo?access_token=%s&openid=%s&lang=zh_CN" % (access_token, open_id)
    response = urllib.request.urlopen(url)

    # 读取微信传回的json响应体数据
    user_json_str = response.read()
    user_dict_data = json.loads(user_json_str)

    if "errcode" in user_dict_data:
        return u"获取用户信息失败"

    # 将用户的资料数据填充到页面中
    return render_template("index.html", user=user_dict_data)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80, debug=True)

'''https://open.weixin.qq.com/connect/oauth2/authorize?appid=wxbb8a530a254f3aa8&redirect_uri=http://3v5s579241.wicp.vip/index&response_type=code&scope=snsapi_userinfo&state=STATE#wechat_redirect'''

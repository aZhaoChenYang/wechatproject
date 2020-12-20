
from flask import Flask, request, abort
import hashlib

# 常量
# 微信的token令牌
WECHAT_TOKEN = "itcast"

app = Flask(__name__)

@app.route("/")
def wechat():
    """对接微信公众号服务器"""
    signature = request.args.get("signature")
    timestamp = request.args.get("timestamp")
    nonce = request.args.get("nonce")
    echostr = request.args.get("echostr")

    # 效验参数
    if not all([signature, timestamp, nonce, echostr]):
        abort(400)

    # 按照微信的流程进行计算签名
    li = [WECHAT_TOKEN, timestamp, nonce]
    # 排序
    li.sort()
    # 拼接字符串
    temp_str = "".join(li)
    # 进行sha1加密, 得到正确的签名值
    sign = hashlib.sha1(temp_str).hexdigest()

    # 将自己计算的签名值与请求的签名参数进行对比,如果相同,则证明请求来自微信服务器
    if signature != sign:
        # 表示请求不是微信发的
        abort(403)
    else:
        return echostr




if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=True)



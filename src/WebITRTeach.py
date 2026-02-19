#!/usr/bin/env python 
# -*- coding:utf-8 -*-

#
# 公式识别 WebAPI 接口
# 使用方法：
#     recognizer = FormulaRecognizer(appid, api_key, secret)
#     result = recognizer.recognize("图片路径")
# 

import requests
import datetime
import hashlib
import base64
import hmac
import json

class FormulaRecognizer(object):
    def __init__(self, appid, api_key, secret, host="rest-api.xfyun.cn"):
        self.APPID = appid
        self.APIKey = api_key
        self.Secret = secret
        self.Host = host
        self.RequestUri = "/v2/itr"
        self.url = "https://" + host + self.RequestUri
        self.HttpMethod = "POST"
        self.Algorithm = "hmac-sha256"
        self.HttpProto = "HTTP/1.1"
        self.BusinessArgs = {
            "ent": "teach-photo-print",
            "aue": "raw",
        }

    def imgRead(self, path):
        with open(path, 'rb') as fo:
            return fo.read()

    def hashlib_256(self, res):
        m = hashlib.sha256(bytes(res.encode(encoding='utf-8'))).digest()
        result = "SHA-256=" + base64.b64encode(m).decode(encoding='utf-8')
        return result

    def httpdate(self, dt):
        """
        Return a string representation of a date according to RFC 1123
        (HTTP/1.1).

        The supplied date must be in UTC.

        """
        weekday = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][dt.weekday()]
        month = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep",
                 "Oct", "Nov", "Dec"][dt.month - 1]
        return "%s, %02d %s %04d %02d:%02d:%02d GMT" % (weekday, dt.day, month,
                                                        dt.year, dt.hour, dt.minute, dt.second)

    def generateSignature(self, digest):
        signatureStr = "host: " + self.Host + "\n"
        signatureStr += "date: " + self.Date + "\n"
        signatureStr += self.HttpMethod + " " + self.RequestUri \
                        + " " + self.HttpProto + "\n"
        signatureStr += "digest: " + digest
        signature = hmac.new(bytes(self.Secret.encode(encoding='utf-8')),
                             bytes(signatureStr.encode(encoding='utf-8')),
                             digestmod=hashlib.sha256).digest()
        result = base64.b64encode(signature)
        return result.decode(encoding='utf-8')

    def init_header(self, data):
        digest = self.hashlib_256(data)
        #print(digest)
        sign = self.generateSignature(digest)
        authHeader = 'api_key="%s", algorithm="%s", ' \
                     'headers="host date request-line digest", ' \
                     'signature="%s"' \
                     % (self.APIKey, self.Algorithm, sign)
        #print(authHeader)
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Method": "POST",
            "Host": self.Host,
            "Date": self.Date,
            "Digest": digest,
            "Authorization": authHeader
        }
        return headers

    def get_body(self, image_path):
        audioData = self.imgRead(image_path)
        content = base64.b64encode(audioData).decode(encoding='utf-8')
        postdata = {
            "common": {"app_id": self.APPID},
            "business": self.BusinessArgs,
            "data": {
                "image": content,
            }
        }
        body = json.dumps(postdata)
        return body

    def process_result(self, respData):
        if "data" not in respData or "region" not in respData["data"]:
            return ""
        
        result = ""
        regions = respData["data"]["region"]
        
        for region in regions:
            if region.get("type") == "text" and "recog" in region:
                content = region["recog"].get("content", "")
                
                processed_content = self._process_content(content)
                result += processed_content
        
        return result
    
    def _process_content(self, content):
        import re
        
        latex_pattern = r'ifly-latex-begin(.*?)ifly-latex-end'
        latex_matches = re.findall(latex_pattern, content, re.DOTALL)
        
        if latex_matches:
            for latex in latex_matches:
                latex_clean = latex.strip()
                latex_formula = f'${latex_clean}$'
                content = content.replace(f'ifly-latex-begin{latex}ifly-latex-end', latex_formula)
        
        graph_pattern = r'graph:(\d+)'
        graph_matches = re.findall(graph_pattern, content)
        
        if graph_matches:
            for graph_id in graph_matches:
                content = content.replace(f'graph:{graph_id}', f'[图像{graph_id}]')
        
        return content

    def recognize(self, image_path, return_raw=False):
        curTime_utc = datetime.datetime.utcnow()
        self.Date = self.httpdate(curTime_utc)
        
        if self.APPID == '' or self.APIKey == '' or self.Secret == '':
            raise ValueError('Appid 或APIKey 或APISecret 为空！')
        
        body = self.get_body(image_path)
        headers = self.init_header(body)
        
        response = requests.post(self.url, data=body, headers=headers, timeout=8)
        status_code = response.status_code
        
        if status_code != 200:
            raise Exception(f"Http请求失败，状态码：{status_code}，错误信息：{response.text}")
        
        respData = json.loads(response.text)
        code = str(respData.get("code", ""))
        
        if code != '0':
            error_msg = respData.get("message", "未知错误")
            raise Exception(f"API调用失败，错误码：{code}，错误信息：{error_msg}")
        
        if return_raw:
            return respData
        
        return self.process_result(respData)

    def call_url(self, image_path="itr/2.jpg"):
        if self.APPID == '' or self.APIKey == '' or self.Secret == '':
            print('Appid 或APIKey 或APISecret 为空！请打开demo代码，填写相关信息。')
        else:
            body = self.get_body(image_path)
            headers = self.init_header(body)
            response = requests.post(self.url, data=body, headers=headers, timeout=8)
            status_code = response.status_code
            if status_code != 200:
                print("Http请求失败，状态码：" + str(status_code) + "，错误信息：" + response.text)
            else:
                respData = json.loads(response.text)
                print(respData)
                code = str(respData.get("code", ""))
                if code != '0':
                    print("请前往https://www.xfyun.cn/document/error-code?code=" + code + "查询解决办法")
                else:
                    formula = self.process_result(respData)
                    print("\n识别结果（处理后的公式）：")
                    print(formula)

if __name__ == '__main__':
    APPID = "bd6d7a3c"
    APIKey = "ca854ccd4fa3c72a8ea1b0fbf3afac1c"
    Secret = "MTEzNjZlZDZhMTVjYTRiM2NiMmU3YzQz"
    
    recognizer = FormulaRecognizer(APPID, APIKey, Secret)
    
    image_path = "D:/ocr_test.jpg"
    
    try:
        result = recognizer.recognize(image_path)
        print("识别结果：")
        print(result)
    except Exception as e:
        print(f"识别失败：{e}")

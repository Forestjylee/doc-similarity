'''
实现加密功能
对明文字符串进行加密
@:param  source_string
by: Junyi
'''

import base64# 使用base64简单加密


# 加密
def encrypt(source_string):
    encrypted_string = base64.b64encode(source_string.encode('utf-8'))
    return str(encrypted_string, 'utf-8')

# 解密
def decrypt(encrypted_string):
    source_string = base64.b64decode(bytes(encrypted_string, encoding='utf-8'))
    return str(source_string, encoding='utf-8')


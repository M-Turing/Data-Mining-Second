# __author__ = 'Administrator'


import hashlib



def get_md5(url):
    if isinstance(url,str):  # 判断参数是否为unicode编码，如果是unicode编码，则将其变为utf-8编码，因为hashlib不接受Unicode编码！1
        url=url.encode('utf-8')
    m=hashlib.md5()
    m.update(url)
    return m.hexdigest()


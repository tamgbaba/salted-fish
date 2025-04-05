import socket
import ssl
import time
import urllib.parse


class Connect:
    _PORT = 443
    _headers: dict = {
        'Host': 'h5api.m.goofish.com',  # 必须保留 Host 头
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'
    }
    _cookie: str
    _ssock = None

    # 秒杀接口
    def sent_seckill_request(self):
        pass

    # 读取响应数据，单词读取仅返回 1400 需要大约是1.5kb
    def read_data(self) -> str:
        return self._ssock.recv(1400).decode('utf-8')

    # 暴露销毁类方法
    def close_connect(self):
        self.__del__()

    # 将字典类型cookie转换为字符串
    def dict_to_cookie_string(self, cookie_dict: dict):
        return '; '.join(f"{key}={value}" for key, value in cookie_dict.items()) + ';'

    def createRequestParams(self, cookies: dict, params: dict, data: dict,
                            timestamp: str = str(round(time.time() * 1000))) -> dict:
        params['sign'] = CustomMD5.md5(
            cookies['_m_h5_tk'].split('_')[0] + "&" + timestamp + "&" + params['appKey'] + "&" + data['data'])
        params['t'] = timestamp
        return params

    # 类销毁的时候需要关闭socket连接
    def __del__(self):
        self._ssock.close()


class Ipv6Connect(Connect):
    # 目标 IPv6 地址和端口 (需提前通过CDN绕过获取真实IP)
    _TARGET_IPV6: list = ['2408:4001:f00::198', '2408:4001:f00::b9']

    def __init__(self, ip_index: int = 0):
        # 1. 创建 IPv6 TCP Socket
        sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
        # 2. 连接目标服务器
        sock.connect((self._TARGET_IPV6[ip_index], self._PORT, 0, 0))
        # 3. 封装为 SSL/TLS 连接（HTTPS）
        context = ssl.create_default_context()
        context.check_hostname = False  # 跳过主机名验证（加速）
        context.verify_mode = ssl.CERT_NONE  # 跳过证书验证
        self._ssock = context.wrap_socket(sock, server_hostname="h5api.m.goofish.com")

    # 发送秒杀请求
    def sent_seckill_request(self, api: str, params: dict, data: dict, cookies: dict):
        headers = self._headers

        # 构建请求体
        def structure_body():
            query_str = '&'.join([f"{k}={v}" for k, v in
                                  self.createRequestParams(cookies=cookies, params=params, data=data,
                                                           timestamp=str(round(time.time() * 1000))).items()])
            path = f"{api}?{query_str}"
            # 对 data 进行 URL 编码
            data_encoded = urllib.parse.urlencode(data)
            content_length = len(data_encoded.encode('utf-8'))
            return (
                f"POST {path} HTTP/1.1\r\n"
                f"Host: {headers['Host']}\r\n"
                f"User-Agent: {headers['User-Agent']}\r\n"
                f"Content-Type: {headers['Content-Type']}\r\n"
                f"Cookie: {self.dict_to_cookie_string(cookies)}\r\n"
                f"Content-Length: {content_length}\r\n"
                "\r\n"
                f"{data_encoded}"
            ).encode('utf-8')

        self._ssock.sendall(structure_body())


class Ipv4Connect(Connect):
    # 目标 IPv6 地址和端口 (需提前通过CDN绕过获取真实IP)
    TARGET_IPV6: list = ['59.82.58.67', ]
    PORT: int = 443

    def _init_(self, ip_index: int = 0):
        # 1. 创建 IPv4 TCP Socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


class CustomMD5:
    @staticmethod
    def md5(a):
        def left_rotate(x, c):
            return (x << c | x >> (32 - c)) & 0xFFFFFFFF

        def add_unsigned(a, b):
            a &= 0xFFFFFFFF
            b &= 0xFFFFFFFF
            return (a + b) & 0xFFFFFFFF

        def F(x, y, z):
            return (x & y) | (~x & z)

        def G(x, y, z):
            return (x & z) | (y & ~z)

        def H(x, y, z):
            return x ^ y ^ z

        def I(x, y, z):
            return y ^ (x | ~z)

        def transform(func, a, b, c, d, x, s, ac):
            a = add_unsigned(a, add_unsigned(func(b, c, d), add_unsigned(x, ac)))
            a = left_rotate(a, s)
            return add_unsigned(a, b)

        def preprocess(input_string):
            input_bytes = bytearray(input_string, "utf-8")
            original_len_in_bits = len(input_bytes) * 8
            input_bytes.append(0x80)

            while len(input_bytes) % 64 != 56:
                input_bytes.append(0)

            input_bytes += original_len_in_bits.to_bytes(8, byteorder="little")
            return input_bytes

        def to_hex(value):
            return "".join(["{:02x}".format((value >> (8 * i)) & 0xFF) for i in range(4)])

        def md5_core(input_bytes):
            A = 0x67452301
            B = 0xEFCDAB89
            C = 0x98BADCFE
            D = 0x10325476

            S = [
                7, 12, 17, 22,
                5, 9, 14, 20,
                4, 11, 16, 23,
                6, 10, 15, 21
            ]

            K = [
                0xd76aa478, 0xe8c7b756, 0x242070db, 0xc1bdceee,
                0xf57c0faf, 0x4787c62a, 0xa8304613, 0xfd469501,
                0x698098d8, 0x8b44f7af, 0xffff5bb1, 0x895cd7be,
                0x6b901122, 0xfd987193, 0xa679438e, 0x49b40821,
                0xf61e2562, 0xc040b340, 0x265e5a51, 0xe9b6c7aa,
                0xd62f105d, 0x02441453, 0xd8a1e681, 0xe7d3fbc8,
                0x21e1cde6, 0xc33707d6, 0xf4d50d87, 0x455a14ed,
                0xa9e3e905, 0xfcefa3f8, 0x676f02d9, 0x8d2a4c8a,
                0xfffa3942, 0x8771f681, 0x6d9d6122, 0xfde5380c,
                0xa4beea44, 0x4bdecfa9, 0xf6bb4b60, 0xbebfbc70,
                0x289b7ec6, 0xeaa127fa, 0xd4ef3085, 0x04881d05,
                0xd9d4d039, 0xe6db99e5, 0x1fa27cf8, 0xc4ac5665,
                0xf4292244, 0x432aff97, 0xab9423a7, 0xfc93a039,
                0x655b59c3, 0x8f0ccc92, 0xffeff47d, 0x85845dd1,
                0x6fa87e4f, 0xfe2ce6e0, 0xa3014314, 0x4e0811a1,
                0xf7537e82, 0xbd3af235, 0x2ad7d2bb, 0xeb86d391
            ]

            blocks = [input_bytes[i:i + 64] for i in range(0, len(input_bytes), 64)]

            for block in blocks:
                X = [int.from_bytes(block[i:i + 4], byteorder="little") for i in range(0, 64, 4)]

                AA, BB, CC, DD = A, B, C, D

                for i in range(64):
                    if 0 <= i <= 15:
                        A = transform(F, A, B, C, D, X[i], S[i % 4], K[i])
                    elif 16 <= i <= 31:
                        A = transform(G, A, B, C, D, X[(1 + 5 * i) % 16], S[4 + i % 4], K[i])
                    elif 32 <= i <= 47:
                        A = transform(H, A, B, C, D, X[(5 + 3 * i) % 16], S[8 + i % 4], K[i])
                    elif 48 <= i <= 63:
                        A = transform(I, A, B, C, D, X[(7 * i) % 16], S[12 + i % 4], K[i])

                    A, B, C, D = D, A, B, C

                A = add_unsigned(A, AA)
                B = add_unsigned(B, BB)
                C = add_unsigned(C, CC)
                D = add_unsigned(D, DD)

            return to_hex(A) + to_hex(B) + to_hex(C) + to_hex(D)

        input_bytes = preprocess(a)
        return md5_core(input_bytes)

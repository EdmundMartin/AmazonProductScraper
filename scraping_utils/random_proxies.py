from random import choice

class RandomProxies:

    def __init__(self, proxy_file=None):
        self.proxies = self.__load_proxy_list(proxy_file)

    def __load_proxy_list(self, proxy_file):
        if proxy_file:
            with open(proxy_file, 'r', encoding='utf-8') as proxy_list:
                return [proxy.strip() if proxy.startswith('http') else 'http://{}'.format(proxy) for proxy in
                        proxy_list]
        else:
            return None

    def get(self):
        if self.proxies:
            return choice(self.proxies)
        else:
            return None

# encoding:utf-8

import plugins
import requests
import json
import pandas as pd
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from common.log import logger
from plugins import *
from datetime import datetime


@plugins.register(
    name="Coin",
    desire_priority=0,
    namecn="币圈行情",
    desc="一个插件用于获取币圈行情",
    version="1.0",
    author="Root",
)
class Coin(Plugin):
    def __init__(self):
        super().__init__()
        self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
        self.active_sessions = {}
        self.options = {
            "1": self.get_altcoin_index,
            "2": self.get_btc_rainbow_chart,
            "3": self.get_fear_greed_index,
            "4": self.get_Dominance,
            "5": self.get_ahr999,
            "6": self.get_crypto_and_fees
        }
        logger.info("[coin] inited")

    def on_handle_context(self, e_context: EventContext):
        if e_context["context"].type != ContextType.TEXT:
            return

        session_id = e_context["context"]["session_id"]
        content = e_context["context"].content
        logger.debug("[coin] on_handle_context. session_id: %s, content: %s" % (session_id, content))
        clist = content.split(maxsplit=1)

        # 检查是否为当前会话的等待回复状态
        if session_id in self.active_sessions:
            if content in self.options:
                message = self.options[content]()
                del self.active_sessions[session_id]  # 清除会话状态
            else:
                message = "无效选项，请选择正确的数字。"

            reply = Reply()
            reply.type = ReplyType.TEXT
            reply.content = message
            e_context["reply"] = reply
            e_context.action = EventAction.BREAK_PASS
            return

        if len(clist) > 0 and clist[0] == "币圈行情":
            message = "请输入数字选择查询对应内容：\n1. 山寨指数\n2. BTC彩虹价格表\n3. 贪婪恐慌指数\n4. BTC/ETH统治力指数\n5. ahr999定投指标\n6. 大饼链gas费"
            self.active_sessions[session_id] = True  # 设置会话状态为等待回复

            reply = Reply()
            reply.type = ReplyType.TEXT
            reply.content = message
            e_context["reply"] = reply
            e_context.action = EventAction.BREAK_PASS

    def get_altcoin_index(self):
        message = '山寨币季度指数是通过比较Top 50加密货币中75%的山寨币在过去90天的表现是否超过比特币来判断的，用以衡量山寨币市场相对于比特币的强势或弱势，其中不包括稳定币和资产支持代币。\n\n'
        url = 'https://www.blockchaincenter.net/altcoin-season-index/'
        response = requests.get(url).text
        response_altcoin_season = response.split('chartdata[90] = ')[1].split(';\n\t\t\t\tchartdata2')[0]
        dic = json.loads(response_altcoin_season)
        df_altcoin_season = pd.DataFrame(dic['values']['all'], index=dic['labels']['all'],
                                         columns=['Altcoin Season'], dtype='float32')
        df_altcoin_season.index = pd.to_datetime(df_altcoin_season.index)
        response_altcoin_month = response.split('chartdata[30] = ')[1].split(';\n\t\t\t\tchartdata2')[0]
        dic = json.loads(response_altcoin_month)
        df_altcoin_month = pd.DataFrame(dic['values']['all'], index=dic['labels']['all'], columns=['Altcoin Month'],
                                        dtype='float32')
        df_altcoin_month.index = pd.to_datetime(df_altcoin_month.index)
        response_altcoin_year = response.split('chartdata[365] = ')[1].split(';\n\t\t\t\tchartdata2')[0]
        dic = json.loads(response_altcoin_year)
        df_altcoin_year = pd.DataFrame(dic['values']['all'], index=dic['labels']['all'], columns=['Altcoin Year'],
                                       dtype='float32')
        df_altcoin_year.index = pd.to_datetime(df_altcoin_year.index)

        message += f'今日山寨币月度指数：{df_altcoin_month.iat[-1, 0]}\n'
        message += f'今日山寨币季度指数：{df_altcoin_season.iat[-1, 0]}\n'
        message += f'今日山寨币年度指数：{df_altcoin_year.iat[-1, 0]}\n'

        return message

    def get_btc_rainbow_chart(self):
        # 获取BTC彩虹价表
        url2 = 'https://www.blockchaincenter.net/bitcoin-rainbow-chart/'
        response2 = requests.get(url2).text

        current_price = response2.split('],\n\t\t\t\t\t\t\t\t\tlabel: "Bitcoin Price"')[0].split('data: [')[-1].replace(
            '"', '').split(',')
        index = len(current_price)  # 4851
        current_price = float(current_price[-1])

        # 价格区间
        # 9850
        price10 = float(
            response2.split('],\n\t\t\t\t\t\t\t\t\tlabel: "Maximum')[0].split('data: [')[-1].split(',')[index - 1])
        price9 = float(
            response2.split('],\n\t\t\t\t\t\t\t\t\tlabel: "Sell. ')[0].split('data: [')[-1].split(',')[index - 1])
        price8 = float(
            response2.split('],\n\t\t\t\t\t\t\t\t\tlabel: "FOMO ')[0].split('data: [')[-1].split(',')[index - 1])
        price7 = float(
            response2.split('],\n\t\t\t\t\t\t\t\t\tlabel: "Is this')[0].split('data: [')[-1].split(',')[index - 1])
        price6 = float(
            response2.split('],\n\t\t\t\t\t\t\t\t\tlabel: "HODL')[0].split('data: [')[-1].split(',')[index - 1])
        price5 = float(
            response2.split('],\n\t\t\t\t\t\t\t\t\tlabel: "Still cheap')[0].split('data: [')[-1].split(',')[index - 1])
        price4 = float(
            response2.split('],\n\t\t\t\t\t\t\t\t\tlabel: "Accumulate')[0].split('data: [')[-1].split(',')[index - 1])
        price3 = float(
            response2.split('],\n\t\t\t\t\t\t\t\t\tlabel: "BUY!')[0].split('data: [')[-1].split(',')[index - 1])
        price2 = float(
            response2.split('],\n\t\t\t\t\t\t\t\t\tlabel: "Basically a fire sale')[0].split('data: [')[-1].split(',')[
                index - 1])
        price1 = float(
            response2.split('],\n\t\t\t\t\t\t\t\t\tlabel: "Below Firesale')[0].split('data: [')[-1].split(',')[
                index - 1])

        price = [price10, price9, price8, price7, price6, price5, price4, price3, price2, price1]
        price = [int(i) for i in price]

        message = '彩虹表是一种通过拟合比特币历史高点和低点来描绘其长期价格走势的有趣图表，旨在提供一种忽略日常波动的视角来观察比特币价格变动，并观察当下BTC处在什么位置。\n\n'
        tag = [''] * 9

        # 根据当前价格生成消息
        if current_price > int(price[0]):
            message += f'今日BTC彩虹价格表：突破天际！！！\n当前BTC价格:{current_price}美元\n'
            pass
        elif current_price > int(price[1]):
            # message += f'今日BTC彩虹价格表：全都是泡沫！！！\n（Maximum Bubble Territory）\n当前BTC价格:{current_price}美元\n'
            message += f'今日BTC彩虹价格表：全都是泡沫！！！\n当前BTC价格:{current_price}美元\n'
            tag[0] = '<———'
        elif current_price > int(price[2]):
            message += f'今日BTC彩虹价格表：卖掉。说认真的，卖掉！\n（Sell. Seriously, SELL!）\n当前BTC价格:{current_price}美元\n'
            message += f'今日BTC彩虹价格表：卖掉。说认真的，卖掉！\n当前BTC价格:{current_price}美元\n'
            tag[1] = '<———'
        elif current_price > int(price[3]):
            # message += f'今日BTC彩虹价格表：FOMO情绪加剧\n（FOMO intensifies）\n当前BTC价格:{current_price}美元\n'
            message += f'今日BTC彩虹价格表：FOMO情绪加剧\n当前BTC价格:{current_price}美元\n'
            tag[2] = '<———'
        elif current_price > int(price[4]):
            # message += f'今日BTC彩虹价格表：这是泡沫吗？\n（Is this a bubble?）\n当前BTC价格:{current_price}美元\n'
            message += f'今日BTC彩虹价格表：这是泡沫吗？\n当前BTC价格:{current_price}美元\n'
            tag[3] = '<———'
        elif current_price > int(price[5]):
            # message += f'今日BTC彩虹价格表：拿住！！！\n（HODL!）\n当前BTC价格：{current_price}美元\n'
            message += f'今日BTC彩虹价格表：拿住！！！\n当前BTC价格：{current_price}美元\n'
            tag[4] = '<———'
        elif current_price > int(price[6]):
            # message += f'今日BTC彩虹价格表：仍然便宜\n（Still cheap）\n当前BTC价格:{current_price}美元\n'
            message += f'今日BTC彩虹价格表：仍然便宜\n当前BTC价格:{current_price}美元\n'
            tag[5] = '<———'
        elif current_price > int(price[7]):
            # message += f'今日BTC彩虹价格表：积攒！\n（Accumulate）\n当前BTC价格：{current_price}美元\n'
            message += f'今日BTC彩虹价格表：积攒！\n当前BTC价格：{current_price}美元\n'
            tag[6] = '<———'
        elif current_price > int(price[8]):
            # message += f'今日BTC彩虹价格表：买买买！\n（BUY!）\n当前BTC价格:{current_price}美元\n'
            message += f'今日BTC彩虹价格表：买买买！\n当前BTC价格:{current_price}美元\n'
            tag[7] = '<———'
        elif current_price > int(price[9]):
            # message += f'基本算清仓大甩卖了！\n（Basically a Fire Sale）\n当前BTC价格：{current_price}美元\n'
            message += f'基本算清仓大甩卖了！\n当前BTC价格：{current_price}美元\n'
            tag[8] = '<———'
        else:
            message += f'今日BTC彩虹价格表：跌破底板了！！！\n当前BTC价格：{current_price}美元\n'

        message += f'FL9：{price[1]}~{price[0]}u{tag[0]}\n'
        message += f'FL8：{price[2]}~{price[1]}u{tag[1]}\n'
        message += f'FL7：{price[3]}~{price[2]}u{tag[2]}\n'
        message += f'FL6：{price[4]}~{price[3]}u{tag[3]}\n'
        message += f'FL5：{price[5]}~{price[4]}u{tag[4]}\n'
        message += f'FL4：{price[6]}~{price[5]}u{tag[5]}\n'
        message += f'FL3：{price[7]}~{price[6]}u{tag[6]}\n'
        message += f'FL2：{price[8]}~{price[7]}u{tag[7]}\n'
        message += f'FL1：{price[9]}~{price[8]}u{tag[8]}\n'

        return message

    def get_crypto_and_fees(self):
        def get_crypto_price(crypto_id):
            url = "https://api.coingecko.com/api/v3/simple/price"
            params = {"ids": crypto_id, "vs_currencies": "usd"}

            response = requests.get(url, params=params)

            if response.status_code == 200:
                data = response.json()
                return data[crypto_id]["usd"]
            else:
                print("Error:", response.status_code)
                print("Response:", response.text)
                return None

        def get_recommended_fees():
            """
            fastestFee:
            这是为了在下一个区块（通常是10分钟内）确认交易而推荐的费用。这是最高的费用率，适用于那些希望他们的交易尽可能快得到确认的用户。

            halfHourFee:
            这个费用是为了在接下来的两个区块（大约半小时内）确认交易而推荐的。它低于fastestFee，适用于可以等待一段较短时间的交易。

            hourFee:
            这是为了在接下来的六个区块（大约1小时内）确认交易而推荐的费用。这个费用适中，适用于对确认时间要求不那么紧迫的交易。

            economyFee:
            这个费用是在交易确认时间可以更长一些时的推荐费用。虽然这个费用较低，但交易可能需要较长时间才能得到确认。

            minimumFee:
            这是被认为是交易可以被网络接受的最低费用。虽然费用最低，但这可能导致交易在被确认之前在内存池中等待很长时间，特别是在网络繁忙时。

            这些费用的选择取决于用户对交易确认时间的需求和愿意支付的费用。在网络繁忙的时候，较高的费用可能是必要的，以确保交易快速得到确认。反之，在网络不那么拥挤的时候，较低的费用可能就足够了。

            """

            url = "https://mempool.space/api/v1/fees/recommended"
            response = requests.get(url)

            if response.status_code == 200:
                original_fees = response.json()

                new_key_mapping = {
                    'fastestFee': '高级',
                    'halfHourFee': '中优先级',
                    'hourFee': '低优先级',
                    'economyFee': '无优先级',
                    'minimumFee': '最低费用'
                }

                # 使用映射创建新字典
                new_fees = {new_key_mapping.get(key, key): value for key, value in original_fees.items()}

                # 将字典转换成字符串
                formatted_fees = "\n".join(f"{key}: {value} sat/vB" for key, value in new_fees.items())
                return formatted_fees
            else:
                return "Error: Unable to fetch data"

        # def set_proxy(proxy):
        #     os.environ['HTTP_PROXY'] = proxy['http']
        #     os.environ['HTTPS_PROXY'] = proxy['https']
        #
        # # 替换 'http://127.0.0.1:23457' 为实际的代理地址
        # proxy_config = {"http": "http://127.0.0.1:23457", "https": "http://127.0.0.1:23457"}
        # set_proxy(proxy_config)

        # 获取比特币价格
        btc_price = get_crypto_price("bitcoin")
        sat_price = btc_price / 100000000  # 1聪的价格

        # 获取推荐交易费用
        recommended_fees = get_recommended_fees()

        # 返回整合的结果
        result = f"BTC当前价格 {btc_price} USDT，每聪 {sat_price} USDT\n推荐Gas费用：\n{recommended_fees}"
        return result

    def get_fear_greed_index(self):
        # 获取贪婪和恐慌指数的URL
        url = 'https://api.alternative.me/fng/?limit=33'
        # 发送HTTP请求并获取响应
        response = requests.get(url).text
        # 将响应文本解析为JSON对象
        response_data = json.loads(response)
        # 提取相关的数据点
        today_value = int(response_data['data'][0]['value'])
        yesterday_value = int(response_data['data'][1]['value'])
        last_week_value = int(response_data['data'][7]['value'])
        last_month_value = int(response_data['data'][30]['value'])

        # 初始化消息字符串
        message = '贪婪&恐慌指数\n'
        message += f'今日贪婪&恐慌指数：{today_value}\n'
        message += f'昨日贪婪&恐慌指数：{yesterday_value}\n'
        message += f'上周贪婪&恐慌指数：{last_week_value}\n'
        message += f'上月贪婪&恐慌指数：{last_month_value}\n'

        # 为每个情绪阶段添加标签
        tag2 = [''] * 5
        if today_value <= 25:
            tag2[0] = '<———'
        elif today_value <= 46:
            tag2[1] = '<———'
        elif today_value <= 54:
            tag2[2] = '<———'
        elif today_value <= 75:
            tag2[3] = '<———'
        else:
            tag2[4] = '<———'

        # 添加情绪阶段到消息字符串
        message += f'情绪：极贪(76~100){tag2[4]}\n'
        message += f'情绪：贪婪(55~75){tag2[3]}\n'
        message += f'情绪：中立(47~54){tag2[2]}\n'
        message += f'情绪：恐慌(26~46){tag2[1]}\n'
        message += f'情绪：极恐(00~25){tag2[0]}\n'

        return message

    def get_Dominance(self):
        url4 = 'https://coinmarketcap.com/charts/'
        response = requests.get(url4).text
        # response = requests.get(url4, proxies).text

        btcDominance = float(
            response.split('"btcDominance":')[1].split(',"btcDominanceChange"')[0])  # 截取文本中的指数并转成float
        ethDominance = float(response.split('"ethDominance":')[1].split(',"etherscanGas"')[0])  # 截取文本中的指数并转成float

        btcDominance = '%.2f%%' % btcDominance
        ethDominance = '%.2f%%' % ethDominance

        message = f'今日BTC/ETH统治力指数：\n'
        message += f'btcDominance：{btcDominance}\n'
        message += f'ethDominance：{ethDominance}\n'
        print(message)

        return message

    def get_ahr999(self):
        message = f'ahr999定投指标\n'
        text = requests.get("https://coinsoto.com/indicatorapi/getAhr999Table", timeout=20).text
        data_dict = json.loads(text)
        value = data_dict['data'][0]['ahr999']
        date = data_dict['data'][0]['date']
        date = datetime.utcfromtimestamp(date / 1000).strftime('%Y-%m-%d')
        message += f'ahr999: {value} ({date})\n'
        message += f'定投线: 1.2 抄底线: 0.45\n'

        return message

    def get_help_text(self, verbose=False, **kwargs):
        short_help_text = " 发送特定指令获取实时的币圈行情数据。\n"

        if not verbose:
            return short_help_text
        help_text = "欢迎使用加密货币市场信息查询功能！\n"
        help_text += "你可以通过输入”币圈行情“ 指令获取特定的市场数据 \n"
        # help_text += "$B 山寨指数，山寨币的月度、季度和年度指数\n"
        # help_text += "$B 彩虹价格表，BTC彩虹价格表的信息\n"
        # help_text += "$B 贪婪恐慌指数，币圈贪婪恐慌指数\n"
        # help_text += "$B 统治力指数，今日BTC/ETH统治力指数\n"
        # help_text += "$B ahr999，比特币ahr999定投指标\n"
        return help_text

try:
    prediction 			= stock["predictions"]["basic"][index]
    current_action  	= prediction["action"]["current"]
    previouse_action	= prediction["action"]["previouse"]
    action_flags 		= prediction["action_flags"]

    key = int("".join(str(x) for x in action_flags), 2)

    send_mail = False
    map_action = {
        0: "none",
        1: "none",
        2: "unknown",
        3: "sell",
        4: "none",
        5: "none",
        6: "buy",
        7: "none"
    }

    if "sell" in current_action:
        if "sell" in map_action[key]:
            action_flags[2] = 0
            # Send mail changed to sell
            send_mail = True
        action_flags[0] = 1
    elif "hold" in current_action:
        action_flags[1] = 1
        # FEATURE: Were from you arrived (buy or sell)
    elif "buy" in current_action:
        if "buy" in map_action[key]:
            action_flags[0] = 0
            # Send mail changed to buy
            send_mail = True
        action_flags[2] = 1
    else:
        pass

    if send_mail is True:
        self.Node.LogMSG("({classname})# [StockSimplePredictionChangeEvent] Send Mail ({0} {1} {2} {3})".format(ticker, stock["price"], previouse_action, current_action, classname=self.ClassName),5)
        html = '''
            <table>
                <tr>
                    <td><span>Ticker</span></td>
                    <td><span>{0}</span></td>
                </tr>
                <tr>
                    <td><span>Price</span></td>
                    <td><span>{1}</span></td>
                </tr>
                <tr>
                    <td><span>Previouse Prediction</span></td>
                    <td><span>{2}</span></td>
                </tr>
                <tr>
                    <td><span>Current Prediction</span></td>
                    <td><span>{3}</span></td>
                </tr>
            </table>
        '''.format(ticker, stock["price"], previouse_action, current_action)
        self.Node.SendMail("yevgeniy.kiveisha@gmail.com", "Stock Monitor Prediction Change", html)
except Exception as e:
    self.Node.LogMSG("({classname})# [EXCEPTION] (StockSimplePredictionChangeEvent) {0} {1}".format(ticker,str(e),classname=self.ClassName),5)
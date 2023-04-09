from yoomoney import Authorize
#https://www.youtube.com/watch?v=u5AtW681f0Q
Authorize(
      client_id="FBC564DD6CD701CDE921D27BDF0E97960F3984BD4225706DB6103C9D97321B51",
      redirect_uri="https://t.me/upravitoparser25bot",
      scope=["account-info",
             "operation-history",
             "operation-details",
             "incoming-transfers",
             "payment-p2p",
             "payment-shop",
             ]
      )
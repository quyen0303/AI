class ChessSubscriber:

    def __init__(self, name):
        self.name = name

    def update(self, message, AI, controller):
        print("got message \n" + message)
        controller.drawEvalBar(AI)

class ChessPublisher:

    def __init__(self):
        self.subscribers = set()
    def register(self, who):
        self.subscribers.add(who)
    def unregister(self, who):
        self.subscribers.discard(who)
    def notify(self, message, AI, controller):
        for subscriber in self.subscribers:
            subscriber.update(message, AI, controller)

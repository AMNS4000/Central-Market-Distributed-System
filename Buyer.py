import grpc
import Market_pb2
import Market_pb2_grpc
from concurrent import futures
import uuid
import threading
from collections import defaultdict
prod = defaultdict(list)
buyer = defaultdict(str)
def SearchItem(a,b):
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = Market_pb2_grpc.SearchItemServiceStub(channel)
        response = stub.SearchItemMethod(Market_pb2.Searchitem(prod_name=a,category=b))
        for i in response:
            if (i.res == "Success"):
                print("Product Name:",i.prod_name)
                print("Product ID:",i.itemid)
                print("Product Price:",i.prod_price)
                if (i.category == "1"):
                    print("Product Category: Electronics")
                elif (i.category == "0"):
                    print("Product Category: Fashion")
                elif (i.category == "2"):
                    print("Product Category: Other")
                print("Product Quantity Remaining:",i.quant_rem)
                print("Product Description:",i.description)
                print("Product Seller Address:",i.selladdr)
                print("Product Rating:",i.rating)
            else:
                print("Failure in Product Search")
def BuyItem(id1,quant,addr):
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = Market_pb2_grpc.BuyitemServiceStub(channel)
        response = stub.BuyitemMethod(Market_pb2.Buyitem(itemid=id1,quant=quant,buy_addr=addr))
        if (response.resp):
            print("Success")
        else:
            print("Failure")
def AddtoWishlist(id1,addr):
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = Market_pb2_grpc.AddtoWishlistServiceStub(channel)
        response = stub.AddtoWishlistMethod(Market_pb2.AddtoWishlist(itemid=id1,buy_addr=addr))
        if (response.resp):
            print("Success")
        else:
            print("Failure")
def RateItem(id1,addr,rate):
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = Market_pb2_grpc.RateitemServiceStub(channel)
        response = stub.RateitemMethod(Market_pb2.Rateitem(itemid=id1,buy_addr=addr,rating=rate))
        if (response.resp):
            print("Success")
        else:
            print("Failure")
def Notify(id1,client_addr,server_addr):
    with grpc.insecure_channel(client_addr) as channel:
        stub = Market_pb2_grpc.NotifyServiceStub(channel)
        response = stub.NotifyMethod(Market_pb2.Notify(itemid=id1,client_addr=server_addr))
        if (response.resp):
            print("Success")
        else:
            print("Failure")
def runBuyer():
    cnt = 1
    print("-------------Welcome to the Buyer's Portal------------------")
    while (cnt!=-1):
        print("1. Search for a product")
        print("2. Buy a product")
        print("3. Add to Wishlist")
        print("4. Rate a product")
        print("5. Exit")
        cnt = int(input("Enter your choice:"))
        if (cnt == 1):
            prod_name = input("Enter the product name:")
            print("0. Fashion")
            print("1. Electronics")
            print("2. Other")
            print('3: Any')
            category = int(input("Enter the category of the product:"))
            SearchItem(prod_name,category)
        elif (cnt == 2):
            id1 = int(input("Enter the product id:"))
            quant = int(input("Enter the quantity:"))
            addr = input("Enter your address:")
            BuyItem(id1,quant,addr)
        elif (cnt == 3):
            id1 = int(input("Enter the product id:"))
            addr = input("Enter your address:")
            AddtoWishlist(id1,addr)
        elif (cnt == 4):
            id1 = int(input("Enter the product id:"))
            addr = input("Enter your address:")
            rate = float(input("Enter the rating:"))
            RateItem(id1,addr,rate)
        elif (cnt == 5):
            cnt = -1
            break
class NotifyClientServiceServicer(Market_pb2_grpc.NotifyClientServiceServicer):
    def NotifyClient(self, request, context):
        print("Notification received from the Buyer")
        print("Product ID : ",request.itemid)
        print("Product Price : ",request.prod_price)
        print("Product Quantity : ",request.quant_rem)
        print("Product Seller Address : ",request.selladdr)
        print("Product Description : ",request.description)
        print("Product Rating : ",request.rating)
        if (request.category == "1"):
            print("Product Category : Electronics")
        elif (request.category == "0"):
            print("Product Category : Fashion")
        elif (request.category == "2"):
            print("Product Category : Other")
        print("Product Name : ",request.prod_name)
        print("1. Search for a product")
        print("2. Buy a product")
        print("3. Add to Wishlist")
        print("4. Rate a product")
        print("5. Exit")
        resp1 = Market_pb2.ResponseInfo()
        resp1.resp = True
        return resp1
def notifyserver():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    Market_pb2_grpc.add_NotifyClientServiceServicer_to_server(NotifyClientServiceServicer(), server)
    server.add_insecure_port("localhost:2025")
    server.start()
    server.wait_for_termination()
if __name__ == "__main__":
    thread_buyer = threading.Thread(target=runBuyer)
    thread_buyer_notification_server = threading.Thread(target=notifyserver)
    thread_buyer.start()
    thread_buyer_notification_server.start()
    thread_buyer.join()
    thread_buyer_notification_server.join()
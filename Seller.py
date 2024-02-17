import grpc
import Market_pb2
import Market_pb2_grpc
from concurrent import futures
import uuid
import threading
from collections import defaultdict
prod = defaultdict(str)
seller = defaultdict(str)
addr_sell = ""
def Register(addr1):
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = Market_pb2_grpc.RegisterSellerServiceStub(channel)
        uuid_seller = str(uuid.uuid1())
        seller[addr1] =  uuid_seller
        global addr_sell
        addr_sell = addr1
        response = stub.RegisterSellerMethod(Market_pb2.SellerInfo(addr=addr1,uuid=uuid_seller))
        if (response.Success):
            print("Success")
        else:
            print("Failure")
def SellItem(a,b,c,d,e,f):
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = Market_pb2_grpc.SellItemServiceStub(channel)
        response = stub.SellItemMethod(Market_pb2.SellItem(prodName = a,category=b,quant=c,description=d,selladdr=e,priceperunit=f,uuid=seller[e]))
        if (response.resp == "Success"):
            print("Success")
            print("Unique ID of the product is:",response.itemid)
            prod[a] = response.itemid
        else:
            print("Failure")
def UpdateItemServiceStub(id1,price,quant,saddr):
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = Market_pb2_grpc.UpdateItemServiceStub(channel)
        response = stub.UpdateItemMethod(Market_pb2.updateItem(prodId = id1,prodprice=price,newquant=quant,selladdr=saddr,uuid=seller[saddr]))
        if (response.resp):
            print("Success")
        else:
            print("Failure")
def DeleteItemServiceStub(id1,saddr):
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = Market_pb2_grpc.DeleteItemServiceStub(channel)
        response = stub.DeleteItemMethod(Market_pb2.deleteItem(prodID = id1,selladdr=saddr,uuid=seller[saddr]))
        if (response.resp):
            print("Success")
        else:
            print("Failure")
def DisplaySellerItemsServiceStub(saddr):
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = Market_pb2_grpc.DisplaySellerItemsServiceStub(channel)
        response = stub.DisplaySellerItemsMethod(Market_pb2.DisplaySellerItems(selladdr=saddr,uuid=seller[saddr]))
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
                print("Failure")
                break    
def runSeller():
    print("-------------Welcome to the Seller's Portal------------------")
    ch1 = 1
    while (ch1!=-1):
        print("1. Register as a Seller")
        print("2. Sell Item")
        print("3. Update Item")
        print("4. Delete Item")
        print("5. Display Seller Items")
        print("Enter -1 to exit")
        ch1 = int(input("Enter your choice: "))
        if (ch1 == 1):
            addr1 = input("Enter the address of the seller: ")
            Register(addr1)
        elif (ch1==2):
            a = input("Enter the product name : ")
            b = input("Enter the category: ")
            c = int(input("Enter the quantity: "))
            d = input("Enter the description: ")
            e = input("Enter the seller address: ")
            f = int(input("Enter the price per unit: "))
            SellItem(a,b,c,d,e,f)
        elif (ch1==3):
            id1 = int(input("Enter the product id: "))
            price = int(input("Enter the new price: "))
            quant = int(input("Enter the new quantity: "))
            saddr = input("Enter the seller address: ")
            UpdateItemServiceStub(id1,price,quant,saddr)
        elif (ch1==4):
            id1 = int(input("Enter the product id: "))
            saddr = input("Enter the seller address: ")
            DeleteItemServiceStub(id1,saddr)
        elif (ch1==5):
            saddr = input("Enter the seller address: ")
            DisplaySellerItemsServiceStub(saddr)
        else:
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
        print("1. Register as a Seller")
        print("2. Sell Item")
        print("3. Update Item")
        print("4. Delete Item")
        print("5. Display Seller Items")
        print("Enter -1 to exit")
        resp1 = Market_pb2.ResponseInfo()
        resp1.resp = True
        return resp1
def notifyserver():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    Market_pb2_grpc.add_NotifyClientServiceServicer_to_server(NotifyClientServiceServicer(), server)
    server.add_insecure_port("localhost:2018")
    server.start()
    server.wait_for_termination()
if __name__ == "__main__":
    thread_seller = threading.Thread(target=runSeller)
    thread_seller_notification_server = threading.Thread(target=notifyserver)
    thread_seller.start()
    thread_seller_notification_server.start()
    thread_seller.join()
    thread_seller_notification_server.join()


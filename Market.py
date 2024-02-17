import grpc
import Market_pb2
import Market_pb2_grpc
from concurrent import futures
from collections import defaultdict
seller = defaultdict(str)
prod = defaultdict(list)
buyer_wishlist = defaultdict(list)
ratedict = defaultdict(list)
prod_id = 1
class RegisterSellerServiceServicer(Market_pb2_grpc.RegisterSellerServiceServicer):
    def RegisterSellerMethod(self, request, context):
        seller_addr = request.addr
        seller_uuid = request.uuid
        if (seller_addr not in seller):
            print(f"Seller join request from {seller_addr},uuid:{seller_uuid}")
            seller[seller_uuid] = seller_addr
            resp1 = Market_pb2.ResponseInfo()
            resp1.Success
            return resp1
        else:
            resp1 = Market_pb2.ResponseInfo()
            resp1.Fail
            return resp1
class SellItemServiceServicer(Market_pb2_grpc.SellItemServiceServicer):
     def SellItemMethod(self, request, context):
        prod_name = request.prodName
        category = request.category
        quant = request.quant
        des = request.description
        sell_addr = request.selladdr
        ppu = request.priceperunit
        uuidsell = request.uuid
        if (uuidsell not in seller or seller[uuidsell] != sell_addr):
            resp1 = Market_pb2.ResponseInfoSellItem()
            resp1.resp = "Failure"
            resp1.itemid = -1
            return resp1
        else:
            prod_list = []
            prod_list.append(prod_name)
            prod_list.append(category)
            prod_list.append(quant)
            prod_list.append(des)
            prod_list.append(sell_addr)
            prod_list.append(ppu)
            prod_list.append(uuidsell)
            prod_list.append(0)
            global prod_id
            prod[prod_id] = prod_list
            print(f"SellItem request from {sell_addr}")
            resp1 = Market_pb2.ResponseInfoSellItem()
            resp1.resp = "Success"
            resp1.itemid = prod_id
            prod_id += 1
            return resp1     
class UpdateItemServiceServicer(Market_pb2_grpc.UpdateItemServiceServicer):
    def UpdateItemMethod(self, request, context):
        prod_id = request.prodId
        prod_price = request.prodprice
        new_quant = request.newquant
        sell_addr = request.selladdr
        uuid = request.uuid
        if (uuid not in seller or seller[uuid] != sell_addr):
            resp1 = Market_pb2.ResponseInfo()
            print("Failed 1")
            resp1.resp = False
            return resp1
        else:
            if (prod_id not in prod):
                resp1 = Market_pb2.ResponseInfo()
                resp1.resp = False
                print(prod_id)
                for key in prod:
                    print(key)
                return resp1
            else:
                prod[prod_id][2] = new_quant
                prod[prod_id][5] = prod_price
                resp1 = Market_pb2.ResponseInfo()
                resp1.resp = True
                for key,value in buyer_wishlist.items():
                    for i in value:
                        if (i == prod_id):
                            NotifyServertoClient(prod_id,key)
                return resp1
class DeleteItemServiceServicer(Market_pb2_grpc.DeleteItemServiceServicer):
    def DeleteItemMethod(self, request, context):
        prod_id = request.prodID
        sell_addr = request.selladdr
        uuid = request.uuid
        if (uuid not in seller or seller[uuid] != sell_addr):
            resp1 = Market_pb2.ResponseInfo()
            resp1.resp = False
            return resp1
        else:
            if (prod_id not in prod):
                resp1 = Market_pb2.ResponseInfo()
                resp1.resp = False
                return resp1
            else:
                del prod[prod_id]
                resp1 = Market_pb2.ResponseInfo()
                resp1.resp = True
                return resp1
class DisplaySellerItemsServiceServicer(Market_pb2_grpc.DisplaySellerItemsServiceServicer):
    def DisplaySellerItemsMethod(self, request, context):
        sell_addr = request.selladdr
        uuid = request.uuid
        if (uuid not in seller or seller[uuid] != sell_addr):
            resp1 = Market_pb2.ItemDetails(itemid=-1,prod_price=-1,prod_name="d",category="OTHER",quant_rem=0,selladdr="pklkjk",rating=0,res="Failure")
            yield resp1
        else:
            print(f"DisplaySellerItems request from {sell_addr}")
            for key in prod:
                if (prod[key][4] == sell_addr):
                    if (len(prod[key]) == 7):   
                        resp1 = Market_pb2.ItemDetails(itemid=int(key)
                                                       ,prod_price=int(prod[key][5])
                                                       ,prod_name=str(prod[key][0])
                                                       ,category=int(prod[key][1])
                                                       ,description=str(prod[key][3])
                                                       ,quant_rem=int(prod[key][2])
                                                       ,selladdr=str(prod[key][4])
                                                       ,rating=float(0),
                                                       res="Success")
                        yield resp1
                    elif (len(prod[key]) == 8):
                        resp1 =  Market_pb2.ItemDetails(itemid=int(key)
                                                                ,prod_price=int(prod[key][5])
                                                                ,prod_name=str(prod[key][0])
                                                                ,category=int(prod[key][1])
                                                                ,description=str(prod[key][3])
                                                                ,quant_rem=int(prod[key][2])
                                                                ,selladdr=str(prod[key][4]),
                                                                rating=float(prod[key][7]),
                                                                res="Success")
                        yield resp1
class SearchItemServiceServicer(Market_pb2_grpc.SearchItemServiceServicer):
    def SearchItemMethod(self, request, context):
        prod_name = request.prod_name
        cate = str(request.category)
        if (cate == "1" and prod_name != ""):
            for key in prod:
                print(prod[key])
                if (prod[key][0] == prod_name):
                    resp1 = Market_pb2.ItemDetails(itemid=int(key)
                                                   ,prod_price=int(prod[key][5])
                                                   ,prod_name=str(prod[key][0])
                                                   ,category=int(prod[key][1])
                                                   ,description=str(prod[key][3])
                                                   ,quant_rem=int(prod[key][2])
                                                   ,selladdr=str(prod[key][4]),
                                                   rating=float(prod[key][7]),
                                                   res="Success")
                    yield resp1
        elif (cate == "0" and prod_name != ""):
            for key in prod:
                if (prod[key][0] == prod_name):
                    resp1 = Market_pb2.ItemDetails(itemid=int(key)
                                                   ,prod_price=int(prod[key][5])
                                                   ,prod_name=str(prod[key][0])
                                                   ,category=int(prod[key][1])
                                                   ,description=str(prod[key][3])
                                                   ,quant_rem=int(prod[key][2])
                                                   ,selladdr=str(prod[key][4]),
                                                   rating=float(prod[key][7]),
                                                   res="Success")
                    yield resp1
        elif (cate== "2" and prod_name != ""):
            for key in prod:
                if (prod[key][0] == prod_name):
                    resp1 = Market_pb2.ItemDetails(itemid=int(key)
                                                   ,prod_price=int(prod[key][5])
                                                   ,prod_name=str(prod[key][0])
                                                   ,category=int(prod[key][1])
                                                   ,description=str(prod[key][3])
                                                   ,quant_rem=int(prod[key][2])
                                                   ,selladdr=str(prod[key][4]),
                                                   rating=float(prod[key][7]),
                                                   res="Success")
                    yield resp1
        elif (cate == "3" or prod_name == ""):
            for key in prod:
                    resp1 = Market_pb2.ItemDetails(itemid=int(key)
                                                   ,prod_price=int(prod[key][5])
                                                   ,prod_name=str(prod[key][0])
                                                   ,category=int(prod[key][1])
                                                   ,description=str(prod[key][3])
                                                   ,quant_rem=int(prod[key][2])
                                                   ,selladdr=str(prod[key][4]),
                                                   rating=float(prod[key][7]),
                                                   res="Success")
                    yield resp1
class BuyitemServiceServicer(Market_pb2_grpc.BuyitemServiceServicer):
    def BuyitemMethod(self, request, context):
        prod_id = request.itemid
        quant = request.quant
        buy_addr = request.buy_addr
        if (prod_id not in prod):
            resp1 = Market_pb2.ResponseInfo()
            resp1.resp = False
            return resp1
        else:
            if (prod[prod_id][2] < quant):
                resp1 = Market_pb2.ResponseInfo()
                resp1.resp = False
                return resp1
            else:
                prod[prod_id][2] -= quant
                print(f"BuyItem request {quant} of item{prod_id} from {buy_addr}")
                resp1 = Market_pb2.ResponseInfo()
                NotifyServertoClient(prod_id,prod[prod_id][4])
                resp1.resp = True
                return resp1
class AddtoWishlistServiceServicer(Market_pb2_grpc.AddtoWishlistServiceServicer):
    def AddtoWishlistMethod(self, request, context):
        prod_id = request.itemid
        buy_addr = request.buy_addr
        if (prod_id not in prod):
            resp1 = Market_pb2.ResponseInfo()
            resp1.resp = False
            return resp1
        else:
            print(f"Wishlist request for item{prod_id} from {buy_addr}")
            buyer_wishlist[buy_addr].append(prod_id)
            resp1 = Market_pb2.ResponseInfo()
            resp1.resp = True
            return resp1
class RateitemServiceServicer(Market_pb2_grpc.RateitemServiceServicer):
    def RateitemMethod(self, request, context):
        prod_id = request.itemid
        buy_addr = request.buy_addr
        rating = request.rating
        if (prod_id not in prod):
            resp1 = Market_pb2.ResponseInfo()
            resp1.resp = False
            return resp1
        elif (prod_id in ratedict[buy_addr]):
            resp1 = Market_pb2.ResponseInfo()
            resp1.resp = False
            return resp1
        else:
            if (rating < 0 or rating > 5):
                resp1 = Market_pb2.ResponseInfo()
                resp1.resp = False
                return resp1
            else:
                print(f"{buy_addr} rated item {prod_id} with {rating}")
                prod[prod_id][7] = (prod[prod_id][7] + rating)/2
                resp1 = Market_pb2.ResponseInfo()
                ratedict[buy_addr].append(prod_id)
                resp1.resp = True
                return resp1
def NotifyServertoClient(id1,saddr):
    with grpc.insecure_channel(saddr) as channel:
        stub = Market_pb2_grpc.NotifyClientServiceStub(channel)
        for key in prod:
            if (int(key) == id1):
                response = stub.NotifyClient(Market_pb2.ItemDetails(itemid=int(key)
                                                   ,prod_price=int(prod[key][5])
                                                   ,prod_name=str(prod[key][0])
                                                   ,category=int(prod[key][1])
                                                   ,description=str(prod[key][3])
                                                   ,quant_rem=int(prod[key][2])
                                                   ,selladdr=str(prod[key][4]),
                                                   rating=float(prod[key][7]),
                                                   res="Success"))
                
                if (response.resp):
                    print("Success: Notified to the client")
                else:
                    print("Failure")
                break
def main():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    Market_pb2_grpc.add_RegisterSellerServiceServicer_to_server(RegisterSellerServiceServicer(), server)
    Market_pb2_grpc.add_SellItemServiceServicer_to_server(SellItemServiceServicer(), server)
    Market_pb2_grpc.add_UpdateItemServiceServicer_to_server(UpdateItemServiceServicer(), server)
    Market_pb2_grpc.add_DeleteItemServiceServicer_to_server(DeleteItemServiceServicer(), server)
    Market_pb2_grpc.add_DisplaySellerItemsServiceServicer_to_server(DisplaySellerItemsServiceServicer(), server)
    Market_pb2_grpc.add_SearchItemServiceServicer_to_server(SearchItemServiceServicer(), server)
    Market_pb2_grpc.add_BuyitemServiceServicer_to_server(BuyitemServiceServicer(), server)
    Market_pb2_grpc.add_AddtoWishlistServiceServicer_to_server(AddtoWishlistServiceServicer(), server)
    Market_pb2_grpc.add_RateitemServiceServicer_to_server(RateitemServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    server.wait_for_termination()
main()
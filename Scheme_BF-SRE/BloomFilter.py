import ctypes
import math

class BloomFilter():
    def __init__(self,n:int,p:float):
        self.bitSize=int(-n*math.log(p)/math.pow(math.log(2),2))
        self.hashFuncSize=int(self.bitSize*math.log(2)/n)
        #self.hashFuncSize =5
        self.bitArray=[0]*(self.bitSize)
        #self.H={}

    def hashnum(self):
        return self.hashFuncSize
    def get_index_ij(self,value):
        self.valueCheck(value)
        hash1=value.__hash__()
        hash2=self.unsigned_right_shitf(hash1,16)
        total_tag_index=[]
        for i in range(self.hashFuncSize):
            combinedHash=hash1+i*hash2
            if combinedHash<0:
                combinedHash=~combinedHash
            combinedHash=combinedHash%self.bitSize
            index = int(combinedHash / 1) 
            total_tag_index.append(index)
        return (total_tag_index, hash1)

    def get_bitarray(self):
        return self.bitArray
    def get_bitnum(self):
        return self.bitSize

    def get_hash(self,value):
        '''
         :param value:存入的数据
       '''
        self.valueCheck(value)
        #哈希值的设置参考google布隆过滤器源码
        hash1=value.__hash__()
        hash2=self.unsigned_right_shitf(hash1,16)
        hash_list=[]
        for i in range(self.hashFuncSize):
            combinedHash=hash1+i*hash2
            if combinedHash<0:
                combinedHash=~combinedHash
            combinedHash = combinedHash % self.bitSize
            hash_list.append(combinedHash)
        return hash_list

    def add_tag(self,value):
        '''
        :param value:存入的数据
        '''
        self.valueCheck(value)
        #哈希值的设置参考google布隆过滤器源码
        hash1=value.__hash__()
        hash2=self.unsigned_right_shitf(hash1,16)
        for i in range(self.hashFuncSize):
            combinedHash=hash1+i*hash2
            if combinedHash<0:
                combinedHash=~combinedHash
            combinedHash=combinedHash%self.bitSize
            index=int(combinedHash/1)#位于第index个int元素
            position=combinedHash-index*32#在int中的位置
            self.bitArray[index] =1
            #self.bitArray[index]=self.bitArray[index]|(1<<position)

    def contains(self,value):
        '''
        :param value:判断是否存在的数据
        :return:True or False
        '''
        self.valueCheck(value)
        hash1 = value.__hash__()
        hash2 = self.unsigned_right_shitf(hash1,16)
        for i in range(self.hashFuncSize):
            combinedHash = hash1 + i * hash2
            if combinedHash < 0:
                combinedHash = ~combinedHash
            combinedHash = combinedHash % self.bitSize
            index = int(combinedHash / 1)  # 位于第index个int元素
            position = combinedHash - index * 32  # 在int中的位置
            result = self.bitArray[index]
            #result= self.bitArray[index] & (1 << position)
            if result==0:
                return False
        return True

    def valueCheck(self, value):
        if value != 0 and not value:
            print('value can\'t be None')

    def int_overflow(self,val):
        maxint = 2147483647
        if not -maxint - 1 <= val <= maxint:
            val = (val + (maxint + 1)) % (2 * (maxint + 1)) - maxint - 1
        return val

    #无符号右移
    def unsigned_right_shitf(self,n, i):
        # 数字小于0，则转为32位无符号uint
        if n < 0:
            n = ctypes.c_uint32(n).value
        # 正常位移位数是为正数，但是为了兼容js之类的，负数就右移变成左移好了
        if i < 0:
            return -self.int_overflow(n << abs(i))
        # print(n)
        return self.int_overflow(n >> i)


# if __name__=='__main__':
#     n=100000000
#     p=0.01
#     bf=BloomFilter(n,p)
#     total_size=100000
#     error_count=0
#     for i in range(total_size):
#         bf.put(i)
#     for i in range(total_size):
#         if not bf.contains(i):
#             error_count+=1
#     print('error rate :',float(error_count/total_size) if error_count>0 else 0)

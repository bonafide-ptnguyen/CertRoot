
from core.interact_certifier import get_total_record, retrieve_record, store_record
# from core.file_hasher import process_folder_test
import datetime

def main():
    print(f"  - Total records:       {get_total_record()}") 
    print("------------------------------------\n")

    recordId = 6
    hash_retrieved_hex, block_num, timestamp = retrieve_record(recordId)
    print(f"Verification Record: {recordId}")
    print(f"  - Hash (Hex):         {hash_retrieved_hex}")
    print(f"  - Block Number:       {block_num}")
    print(f"  - Block Timestamp:    {datetime.datetime.fromtimestamp(timestamp)}")
    print("------------------------------------\n")

    # # enable to store a new file. use absolute file path
    # # singleFilePath = "C:\\Users\\gerar\\OneDrive\\Desktop\\temp\\test\\CertRoot\\backend\\files\\frog_modified.png"
    # singleFilePath = "/home/gerard/Software/Blockchain_Web_App/fyp/dev/CertRoot/inputs/test.txt"
    # new_record_Id, digest, tx_hash = store_record(singleFilePath)
    # print(f"  - Record ID :         {new_record_Id}")
    # print(f"  - File hash :         {digest}")
    # print(f"  - transaction hash :       {tx_hash}")
    # print("------------------------------------\n")
    # print(f"  - Total records:       {get_total_record()}") 

    # process_folder_test()

if __name__ == "__main__":
    main()
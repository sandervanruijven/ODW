import read_mail, extract, transform
#import read_mail, extract, transform, load

# Ensure execute.py can only be ran from bash
if __name__ == '__main__':
    # 1. Run Read_mail
    read_mail.main()
    # 2. Run Extract
    extract.main()
    # # 3. Run Transform
    transform.main()
    # # 4. Run Load
    # load.main()
"""
Simple use case for Dataset class.  This should be expanded and show all
    features of Dataset at some point.

"""
from sync.dataset import Dataset


def main():
    """simple data example"""
    dset = Dataset("C:/sync/output/test.h5")
    events = dset.get_all_events()
    print(("Events:", events))

    b0 = dset.get_bit(0)
    print(b0[:20])

    import ipdb

    ipdb.set_trace()


if __name__ == '__main__':
    main()

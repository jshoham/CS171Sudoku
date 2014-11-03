__author__ = 'jshoham'

from src import process_results

if __name__ == '__main__':
    n = 10
    how_many = 100
    directory = 'trials n{} {}'.format(n, how_many)

    t1 = 'bt'
    t2 = 'bt fc'
    t3 = 'bt fc mrv'
    t4 = 'bt fc mrv dh'
    t5 = 'bt fc mrv dh lcv'
    t6 = 'bt fc mrv dh lcv acp'
    t7 = 'bt fc mrv dh lcv acp ac'
    tx = ''


    all_args = ['{}/n{} results {}/*_raw_data*.txt'.format(directory, n, t1),
                '{}/n{} results {}/*_raw_data*.txt'.format(directory, n, t2),
                '{}/n{} results {}/*_raw_data*.txt'.format(directory, n, t3),
                '{}/n{} results {}/*_raw_data*.txt'.format(directory, n, t4),
                '{}/n{} results {}/*_raw_data*.txt'.format(directory, n, t5),
                '{}/n{} results {}/*_raw_data*.txt'.format(directory, n, t6),
                '{}/n{} results {}/*_raw_data*.txt'.format(directory, n, t7),
                '{}/n{} results {}/*_raw_data*.txt'.format(directory, n, tx)
                ]

    for each in all_args:
        process_results.main(each)

# filter function.
# the function must accept 5 args(id, title, author, reply_num, good)
# and return True(if you would like to store this thread..) or False (or not)
# only threads which have more than 0 replies will be stored.


def thread_filter(id, title, author, reply_num, good):
    return reply_num > 0

# > scrapy run hadoop hadoop -f thread_filter


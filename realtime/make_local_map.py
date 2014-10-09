# coding=utf-8
"""Simple helper for when you already have the grid.xml and just want a map."""
#Tim Sutton, April 2013.

from shake_event import ShakeEvent

if __name__ == '__main__':
    import time

    SHAKE_ID = ['20130213112454', '20130216125525', '20130223180922',
                '20130305091435', '20130318105917', '20130404122909',
                '20130409015342', '20130417120953', '20130420115112',
                '20130504133155', '20130524123229', '20130616025542',
                '20130630080909', '20130705235439', '20130714114844',
                '20130720235255', '20130801143052', '20130810185720',
                '20130823020402', '20130910081709', '20130920221321',
                '20131023162008', '20131105060809', '20131119092816',
                '20131202143935', '20131215120851', '20131225094625',
                '20140114212356', '20140123150542', '20140211011056']
    # To ensure that realtime is working for not just en locale, use other
    # locale here to test realtime
    for shake_id in SHAKE_ID:
        start_time = time.time()

        shake_event = ShakeEvent(
            event_id=shake_id,
            locale='en',
            force_flag=False,
            data_is_local_flag=True)
        shake_event.render_map(force_flag=False)

        print '--- Time %s: %s sec' % (shake_id, time.time() - start_time)

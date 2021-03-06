import bz2
import json
import datetime
import collections

import flask
import tzlocal

import dmr.config
import dmr.config.dns
import dmr.models.dns_messages

DNS_BP = flask.Blueprint('dns', __name__, url_prefix='/dns')

@DNS_BP.route('/message', methods=['POST'])
def dns_message():
    data_bz2 = flask.request.get_data()
    data_encoded = bz2.decompress(data_bz2)
    message_list = json.loads(data_encoded)

    dm = dmr.models.dns_messages.DnsMessagesModel()

    for message in message_list:
        timestamp_dt = \
            datetime.datetime.strptime(
                message['timestamp'], 
                dmr.config.DATETIME_FORMAT)

        message['timestamp'] = \
            timestamp_dt.replace(tzinfo=dmr.config.dns.MESSAGE_TZ)

    dm.add_messages(message_list)

    result = {
        'count': len(message_list),
    }

    raw_response = flask.jsonify(result)
    response = flask.make_response(raw_response)

    return (response, 200)

@DNS_BP.route('/ajax/activity/minute', methods=['GET'])
def dns_ajax_activity_by_minute():
    local_tz = tzlocal.get_localzone()
    now_dt = datetime.datetime.now().replace(tzinfo=local_tz)
    delta_td = datetime.timedelta(seconds=dmr.config.dns.ACTIVITY_CUTOFF_S)

    cutoff_dt = now_dt - delta_td

    dm = dmr.models.dns_messages.DnsMessagesModel()
    rows = dm.get_daily_activity_by_minute(cutoff_dt)

    bins = collections.defaultdict(list)
    for (timestamp_t, type_, count) in rows:
        bins[type_].append((timestamp_t, count))

    for type_ in bins.keys():
        bins[type_] = sorted(bins[type_], key=lambda (t, c): t)

    raw_response = flask.jsonify(dict(bins))
    response = flask.make_response(raw_response)

    return (response, 200)

@DNS_BP.route('/ajax/activity/hour', methods=['GET'])
def dns_ajax_activity_by_hour():
    local_tz = tzlocal.get_localzone()
    now_dt = datetime.datetime.now().replace(tzinfo=local_tz)
    delta_td = datetime.timedelta(seconds=dmr.config.dns.ACTIVITY_CUTOFF_S)

    cutoff_dt = now_dt - delta_td

    dm = dmr.models.dns_messages.DnsMessagesModel()
    rows = dm.get_daily_activity_by_hour(cutoff_dt)

    bins = collections.defaultdict(list)
    for (timestamp_t, type_, count) in rows:
        bins[type_].append((timestamp_t, count))

    for type_ in bins.keys():
        bins[type_] = sorted(bins[type_], key=lambda (t, c): t)

    raw_response = flask.jsonify(dict(bins))
    response = flask.make_response(raw_response)

    return (response, 200)

from elasticsearch_dsl import DocType, Search, Date, Integer, Keyword, Text, Ip
from elasticsearch_dsl import connections, InnerDoc, Nested, Object


class DomainDetailsDoc(DocType):
    '''
    Document storage for domain cache
    '''
    name = Text(analyzer='snowball', fields={'raw': Keyword()})
    tags = Keyword()
    doc_created = Date()
    doc_updated = Date()
    processed = Integer()

    class Meta:
        index = 'sfn-domain-details'

    @classmethod
    def get_indexable(cls):
        return cls.get_model().get_objects()

    @classmethod
    def from_obj(cls, obj):
        return cls(
            id=obj.id,
            name=obj.name,
            tags=obj.tags,
            doc_created=obj.doc_created,
            doc_updated=obj.doc_updated,
            processed=obj.processed,
        )

    def save(self, **kwargs):
        return super(DomainDetailsDoc, self).save(**kwargs)


# class EventTag(InnerDoc):
#     '''
#     Tag info that is pushed to sfn-dns-event doc
#     '''
#     tag_name = Text(fields={'raw': Keyword()})
#     public_tag_name = Text(analyzer='snowball')
#     tag_class = Text(fields={'raw': Keyword()})
#     confidence_level = Integer()
#     sample_date = Date()
#     file_type = Text(fields={'raw': Keyword()})

class SFNDNS(InnerDoc):
    event_type = Text()
    domain_name = Text(analyzer='snowball', fields={'raw': Keyword()})
    device_name = Text(analyzer='snowball', fields={'raw': Keyword()})
    host = Text(analyzer='snowball', fields={'raw': Keyword()})
    threat_id = Text(analyzer='snowball')
    threat_name = Text(analyzer='snowball')
    tag_name = Text(fields={'raw': Keyword()})
    public_tag_name = Text(analyzer='snowball')
    tag_class = Text(fields={'raw': Keyword()})
    confidence_level = Integer()
    sample_date = Date()
    file_type = Text(fields={'raw': Keyword()})
    updated_at = Date()
    processed = Integer()
    src_ip = Ip()
    dst_ip = Ip()


class DNSEventDoc(DocType):
    '''
    Each event is it's own entity in the DB. This is the structure of that entitiy
    '''
    SFN = Object(SFNDNS)
    
    class Meta:
         index = 'threat-*'

    @classmethod
    def get_indexable(cls):
        return cls.get_model().get_objects()

    @classmethod
    def from_obj(cls, obj):
        return cls(
            id=obj.id,
            domain_name=obj.domain_name,
            device_name=obj.device_name,
            host=obj.host,
            threat_id=obj.threat_id,
            event_tag=obj.event_tag,
            created_at=obj.created_at,
            updated_at=obj.updated_at,
            processed=obj.processed,
            src_ip=obj.src_ip,
            dst_ip=obj.dst_ip
        )

    def save(self, **kwargs):
        return super(DNSEventDoc, self).save(**kwargs)


class AFDetailsDoc(DocType):
    '''
    Stores the information returned from autofocus about API logistics
    '''
    daily_points = Integer()
    daily_points_remaining = Integer()
    minute_points = Integer()
    minute_points_remaining = Integer()
    minute_bucket_start = Date()
    daily_bucket_start = Date()

    class Meta:
        index = 'af-details'
        id = 'af-details'

    @classmethod
    def get_indexable(cls):
        return cls.get_model().get_objects()

    @classmethod
    def from_obj(cls, obj):
        return cls(
            id=obj.id,
            daily_points=obj.daily_points,
            daily_points_remaining=obj.daily_points_remaining,
            minute_points=obj.minute_points,
            minute_points_remaining=obj.minute_points_remaining,
            daily_bucket_start=obj.daily_bucket_start,
            minute_bucket_start=obj.minute_bucket_start
        )

    def save(self, **kwargs):
        return super(AFDetailsDoc, self).save(**kwargs)


class TagDetailsDoc(DocType):
    '''
    Stores/caches information about each tag in the DB
    '''
    name = Text(analyzer='snowball', fields={'raw': Keyword()})
    tag = Keyword()
    doc_created = Date()
    doc_updated = Date()
    processed = Integer()

    class Meta:
        index = 'sfn-tag-details'

    @classmethod
    def get_indexable(cls):
        return cls.get_model().get_objects()

    @classmethod
    def from_obj(cls, obj):
        return cls(
            id=obj.id,
            name=obj.name,
            tag=obj.tag,
            doc_created=obj.doc_created,
            doc_updated=obj.doc_updated,
            processed=obj.processed,
        )

    def save(self, **kwargs):
        return super(TagDetailsDoc, self).save(**kwargs)

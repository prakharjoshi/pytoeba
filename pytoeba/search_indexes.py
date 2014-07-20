from haystack import indexes
from pytoeba.models import (
    Sentence, LocalizedTag, Comment, WallPost, PytoebaUser, Message
    )
from .utils import now
from nltk import stem
from django.conf import settings
# sample utility class for stemming, tokenizing, and removing stopwords

STEMMERS = {
    'eng': stem.snowball.EnglishStemmer()
}
STEMMERS = getattr(settings, 'HAYSTACK_STEMMERS', STEMMERS)

TOKENIZERS = getattr(settings, 'HAYSTACK_TOKENIZERS', {})

STOP_WORDS = getattr(settings, 'HAYSTACK_STOP_WORDS', {})

class Stemmer(object):

    def __init__(self, lang=None):
        self.lang = lang
        self.stemmer = STEMMERS.get(lang, None)
        self.tokenizer = TOKENIZERS.get(lang, None)
        self.stop_words = set(STOP_WORDS.get(lang, set()))

    def stem(self, text, lang):
        lang = lang or self.lang
        stemmer = STEMMERS.get(lang, None) or self.stemmer

        if not stemmer: return ''

        stemmed_text = []

        for token in self.tokenize(text):
            if token not in self.stop_words:
                token = stemmer.stem(token)
                stemmed_text.append(token)

        stemmed_text = ' '.join(stemmed_text)

        return stemmed_text

    def tokenize(self, text):
        tokenizer = self.tokenizer if self.tokenizer else lambda s: s.split()

        for token in tokenizer(text):
            yield token

stemmer = Stemmer()

class SentenceIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True)
    hash_id = indexes.CharField(model_attr='hash_id')
    sentence_text = indexes.CharField(model_attr='text')
    sentence_text_stemmed = indexes.CharField()
    added_by = indexes.CharField()
    added_on = indexes.DateTimeField(model_attr='added_on')
    modified_on = indexes.DateTimeField(model_attr='modified_on')
    owner = indexes.CharField()
    is_editable = indexes.BooleanField(model_attr='is_editable')
    length = indexes.IntegerField(model_attr='length')

    def get_model(self):
        return Sentence

    def index_queryset(self, using=None):
        return self.get_model().objects.active().filter(modified_on__lte=now())

    def prepare(self, object):
        self.prepared_data = super(SentenceIndex, self).prepare(object)

        self.prepared_data['added_by'] = object.added_by.username
        self.prepared_data['owner'] = object.owner.username

        self.prepared_data['sentence_text_stemmed'] = stemmer.stem(object.text, object.lang)

        return self.prepared_data


class TagIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True)
    tag_id = indexes.IntegerField(model_attr='tag_id')
    tag_text = indexes.CharField(model_attr='text')

    def get_model(self):
        return LocalizedTag

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(tag__added_on__lte=now())

    def prepare(self, object):
        self.prepared_data = super(TagIndex, self).prepare(object)

        self.prepared_data['tag_id'] = object.tag_id

        return self.prepared_data


class CommentIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True)
    sentence_id = indexes.IntegerField(model_attr='sentence_id')
    comment_text = indexes.CharField(model_attr='text')
    added_by = indexes.CharField(model_attr='added_by')
    added_on = indexes.DateTimeField(model_attr='added_on')

    def get_model(self):
        return Comment

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(
            is_public=True, is_deleted=False, modified_on__lte=now()
            )

    def prepare(self, object):
        self.prepared_data = super(CommentIndex, self).prepare(object)

        self.prepared_data['sentence_id'] = object.sentence_id
        self.prepared_data['added_by'] = object.added_by.username

        return self.prepared_data


class WallIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True)
    wall_id = indexes.IntegerField()
    thread_id = indexes.IntegerField()
    post_id = indexes.IntegerField()
    wall_category = indexes.CharField()
    thread_subject = indexes.CharField()
    thread_is_sticky = indexes.BooleanField()
    thread_subscribers = indexes.CharField()
    thread_op = indexes.CharField()
    post_subject = indexes.CharField(model_attr='subject')
    post_text = indexes.CharField(model_attr='body_text')
    poster = indexes.CharField()
    added_on = indexes.DateTimeField(model_attr='added_on')
    modified_on = indexes.DateTimeField(model_attr='modified_on')

    def get_model(self):
        return WallPost

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(
            is_public=True, modified_on__lte=now()
            )

    def prepare(self, object):
        self.prepared_data = super(WallIndex, self).prepare(object)

        self.prepared_data['wall_id'] = object.wall_id
        self.prepared_data['thread_id'] = object.thread_id
        self.prepared_data['post_id'] = object.id
        self.prepared_data['wall_category'] = object.wall.category
        self.prepared_data['thread_subject'] = object.thread.subject
        self.prepared_data['thread_is_sticky'] = object.thread.sticky
        self.prepared_data['thread_subscribers'] = ' '.join([
        subscriber.username
        for subscriber in list(object.thread.subscribers.all())
        ])
        self.prepared_data['thread_op'] = object.thread.added_by.username
        self.prepared_data['poster'] = object.added_by.username

        return self.prepared_data


class UserIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True)
    user_id = indexes.IntegerField(model_attr='id')
    username = indexes.CharField(model_attr='username')
    first_name = indexes.CharField(model_attr='first_name')
    last_name = indexes.CharField(model_attr='last_name')
    date_joined = indexes.DateTimeField(model_attr='date_joined')
    privacy = indexes.CharField(model_attr='privacy')
    status = indexes.CharField(model_attr='status')
    country = indexes.CharField(model_attr='country')
    birthday = indexes.DateTimeField(model_attr='birthday')
    about = indexes.CharField(model_attr='about_text')

    def get_model(self):
        return PytoebaUser

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(
            email_unconfirmed='', date_joined__lte=now()
            )


class MessageIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True)
    message_id = indexes.IntegerField(model_attr='id')
    subject = indexes.CharField(model_attr='subject')
    body = indexes.CharField(model_attr='body')
    sender = indexes.CharField()
    recipient = indexes.CharField()
    parent_id = indexes.IntegerField()
    sent_on = indexes.DateTimeField(model_attr='sent_on')
    read_on = indexes.DateTimeField(model_attr='read_on')
    replied_on = indexes.DateTimeField(model_attr='replied_on')
    sent_on = indexes.DateTimeField(model_attr='sent_on')
    sender_deleted_on = indexes.DateTimeField(model_attr='sender_deleted_on')
    recipient_deleted_on = indexes.DateTimeField(model_attr='recipient_deleted_on')

    def get_model(self):
        return Message

    def index_queryset(self, using=None):
        return self.get_model().objects.filter(sent_on__lte=now())

    def prepare(self, object):
        self.prepared_data = super(MessageIndex, self).prepare(object)

        self.prepared_data['sender'] = object.sender.username
        self.prepared_data['recipient'] = object.recipient.username
        self.prepared_data['parent_id'] = object.parent_msg.id

        return self.prepared_data

from django.db.models.manager import Manager
from django.db.models.query import QuerySet
from django.db.models.loading import get_model

from .utils import get_user, now, bulk_update, bulk_create, bulk_delete


class SentenceQuerySet(QuerySet):
    """
    Overrides django's default queryset class to add
    custom fuctionality mirrored from instance methods
    and on the manager. This essentially means every
    time you apply any orm filter these methods will
    be available on them, which makes them chainable.
    """
    def all(self):
        """
        This makes all other filters not see deleted
        objects by default.
        """
        return self.filter(is_deleted=False)

    def deleted(self):
        """
        This filter shows only deleted objects.
        """
        return self.filter(is_deleted=True)

    def active(self):
        """
        A filter that shows only objects that have been
        owned by a native or someone with the appropriate
        permissions for is_active to be true.
        """
        return self.all().filter(is_active=True)

    def inactive(self):
        """
        Reverse fucntionality of the active filter.
        """
        return self.all().filter(is_active=False)

    def locked(self):
        """
        Filters all locked sentences.
        """
        return self.all().filter(is_editable=False)

    def unlocked(self):
        """
        Reverse filter for locked.
        """
        return self.all().filter(is_editable=True)

    def orphan(self):
        """
        Filters all unowned sentences.
        """
        return self.all().filter(owner=None)

    def needs_correction(self):
        """
        Filters all sentences that have an attached correction.
        """
        return self.all().filter(has_correction=True)

    def delete(self):
        """
        Bulk deletes all sentences in the queryset. Uses the
        same implementation as the delete sentence instance
        method.
        """
        user = get_user()
        sents = list(self.all())
        logs = []
        Log = get_model('pytoeba', 'Log')

        for sent in sents:
            sent.is_deleted = True
            logs.append(
                Log(
                    sentence=sent, type='srd', done_by=user,
                    source_hash_id=sent.hash_id, source_lang=sent.lang
                    )
                )

        bulk_update(sents, update_fields=['is_deleted'])
        bulk_create(logs)

    def lock(self):
        """
        Bulk locks sentences in the queryset. Mirrors
        sentence.lock
        """
        user = get_user()
        sents = list(self.all())
        logs = []
        Log = get_model('pytoeba', 'Log')

        for sent in sents:
            sent.is_editable = False
            logs.append(
                Log(
                    sentence=sent, type='sld', done_by=user,
                    source_hash_id=sent.hash_id, source_lang=sent.lang
                    )
                )

        bulk_update(sents, update_fields=['is_editable'])
        bulk_create(logs)

    def unlock(self):
        """
        Bulk unlocks sentences in the queryset. Mirrors
        sentece.lock.
        """
        user = get_user()
        sents = list(self.all())
        logs = []
        Log = get_model('pytoeba', 'Log')

        for sent in sents:
            sent.is_editable = True
            logs.append(
                Log(
                    sentence=sent, type='sul', done_by=user,
                    source_hash_id=sent.hash_id, source_lang=sent.lang
                    )
                )

        bulk_update(sents, update_fields=['is_editable'])
        bulk_create(logs)

    def adopt(self):
        """
        Bulk adopts sentences in the queryset. Mirrors
        sentence.adopt.
        """
        user = get_user()
        sents = list(self.all())
        logs = []
        Log = get_model('pytoeba', 'Log')

        for sent in sents:
            sent.owner = user
            logs.append(
                Log(
                    sentence=sent, type='soa', done_by=user,
                    source_hash_id=sent.hash_id, source_lang=sent.lang
                    )
                )

        bulk_update(sents, update_fields=['owner'])
        bulk_create(logs)

    def release(self):
        """
        Bulk releases ownership over sentences in the
        queryset. Mirrors sentence.release.
        """
        user = get_user()
        sents = list(self.all())
        logs = []
        Log = get_model('pytoeba', 'Log')

        for sent in sents:
            sent.owner = None
            logs.append(
                Log(
                    sentence=sent, type='sor', done_by=user,
                    source_hash_id=sent.hash_id, source_lang=sent.lang
                    )
                )

        bulk_update(sents, update_fields=['owner'])
        bulk_create(logs)

    def change_language(self, lang):
        """
        Bulk changes the lang field on sentences in the
        queryset. Mirrors sentence.change_language.
        """
        user = get_user()
        sents = list(self.all())
        logs = []
        Log = get_model('pytoeba', 'Log')

        for sent in sents:
            old_lang = sent.lang
            sent.lang = lang
            logs.append(
                Log(
                    sentence=sent, type='slc', done_by=user,
                    source_hash_id=sent.hash_id, source_lang=old_lang,
                    target_lang=sent.lang
                    )
                )

        bulk_update(sents, update_fields=['lang'])
        bulk_create(logs)

    def link(self, sent):
        """
        Links all sentences in the
        queryset to a single sentence.
        Mirrors the instance method.
        """
        sents = list(self.all())
        sent.bulk_link(sents)

    def unlink(self, sent):
        """
        Unlinks all sentences in the
        queryset from a single sentence.
        Mirrors the instance methods.
        """
        sents = list(self.all())
        sent.bulk_unlink(sents)

    def translate(self, text, lang='auto'):
        """
        Adds a sentence then links it to
        all sentences in the queryset.
        Mirrors the instance methods.
        """
        sents = list(self.all())
        sent = self.add(text, lang)
        sent.bulk_link(sents)


class SentenceManager(Manager):

    def get_query_set(self):
        return SentenceQuerySet(self.model, using=self._db)

    def all(self):
        return self.get_query_set().all()

    def deleted(self):
        return self.get_query_set().deleted()

    def active(self):
        return self.get_query_set().active()

    def inactive(self):
        return self.get_query_set().active()

    def locked(self):
        return self.get_query_set().locked()

    def unlocked(self):
        return self.get_query_set().unlocked()

    def orphan(self):
        return self.get_query_set().orphan()

    def needs_correction(self):
        return self.get_query_set().needs_correction()

    def add(self, text, lang='auto'):
        user = get_user()
        sent = self.create(
            added_by=user, owner=user, text=text, lang=lang
            )
        Log = get_model('pytoeba', 'Log')
        Log.objects.create(
            sentence=sent, type='sad', done_by=user, change_set=text,
            target_id=sent.id, target_hash_id=sent.hash_id
            )
        return sent

    def bulk_add(self, sentences):
        added_sents = []
        
        if isinstance(sentences[0], dict):
            for sent_info in sentences:
                text = sent_info['text']
                lang = sent_info['lang']
                sent = self.add(text, lang)
                added_sents.append(sent)
        else:
            for sentence in sentences:
                sent = self.add(sentence)
                added_sents.append(sent)

        return added_sents

    def show(self, hash_id):
        return self.get(hash_id=hash_id)

    def bulk_show(self, hashes):
        return self.filter(hash_id__in=hashes)

    def edit(self, hash_id, text):
        sent = self.show(hash_id)
        sent.edit(text)

    def delete(self, hash_id):
        sent = self.show(hash_id)
        sent.delete()

    def bulk_delete(self, hashes):
        self.bulk_show(hashes).delete()

    def lock(self, sent_id):
        self.show(sent_id)
        sent.lock()

    def unlock(self, sent_id):
        self.show(sent_id)
        sent.unlock()

    def adopt(self, sent_id):
        self.show(sent_id)
        sent.adopt()

    def release(self, sent_id):
        self.show(sent_id)
        sent.release()

    def link(self, source_id, target_id):
        source = self.show(source_id)
        target = self.show(target_id)
        source.link(target)

    def bulk_link(self, source_id, target_ids):
        source = self.show(source_id)
        targets = self.bulk_show(target_ids)
        source.bulk_link(targets)

    def unlink(self, source_id, target_id):
        source = self.show(source_id)
        target = self.show(target_id)
        source.unlink(target)

    def bulk_unlink(self, source_id, target_ids):
        source = self.show(source_id)
        targets = self.bulk_show(target_ids)
        source.bulk_unlink(targets)

    def translate(self, sent_id, text, lang='auto'):
        sent = self.show(sent_id)
        sent.translate(text, lang)

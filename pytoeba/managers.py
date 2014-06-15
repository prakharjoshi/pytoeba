from django.db.models.manager import Manager
from django.db.models.query import QuerySet
from django.db.models.loading import get_model
from django.contrib.auth.models import UserManager
from django.contrib.auth import authenticate

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

    def auto_force_correction(self):
        """
        Autoforces corrections on all sentences
        in the queryset. Mirrors the instance method.
        """
        user = get_user()
        sents = list(self.all())
        logs = []
        Log = get_model('pytoeba', 'Log')
        Correction = get_model('pytoeba', 'Correction')

        for sent in sents:
            corr = Correction.objects.filter(sentence=sent)[0]
            sent.text = corr.text
            logs.append(
                Log(
                    sentence=sent, type='cfd', done_by=user, change_set=corr.text,
                    source_hash_id=sent.hash_id, source_lang=sent.lang,
                    target_id=corr.id, target_hash_id=corr.hash_id
                    )
                )

        bulk_update(sents, update_fields=['text'])
        bulk_create(logs)

    def add_tag(self, text):
        """
        Adds an existing tag to all sentences
        in the queryset. Mirrors the instance
        method.
        """
        user = get_user()
        sents = list(self.all())
        sentags = []
        logs = []
        Log = get_model('pytoeba', 'Log')
        LocalizedTag = get_model('pytoeba', 'LocalizedTag')
        SentenceTag = get_model('pytoeba', 'SentenceTag')
        tag = LocalizedTag.objects.get(text=text).tag

        for sent in sents:
            sentags.append(
                SentenceTag(
                    sentence=sent, tag=tag, added_by=user
                    )
                )
            logs.append(
                Log(
                    sentence=sent, type='cfd', done_by=user, change_set=corr.text,
                    source_hash_id=sent.hash_id, source_lang=sent.lang,
                    target_id=corr.id, target_hash_id=corr.hash_id
                    )
                )

        bulk_create(sentags)
        bulk_create(logs)

    def add_new_tag(self, text, lang):
        """
        Creates a new tag then adds it to all
        sentences in the queryset. Mirrors the
        instance method.
        """
        user = get_user()
        sents = list(self.all())
        sentags = []
        logs = []
        Log = get_model('pytoeba', 'Log')
        Tag = get_model('pytoeba', 'Tag')
        SentenceTag = get_model('pytoeba', 'SentenceTag')
        tag = Tag.objects.add_new(text, lang)

        for sent in sents:
            sentags.append(
                SentenceTag(
                    sentence=sent, tag=tag, added_by=user
                    )
                )
            logs.append(
                Log(
                    sentence=sent, type='cfd', done_by=user, change_set=corr.text,
                    source_hash_id=sent.hash_id, source_lang=sent.lang,
                    target_id=corr.id, target_hash_id=corr.hash_id
                    )
                )

        bulk_create(sentags)
        bulk_create(logs)

    def delete_tag(self, text):
        """
        Removes a tag from all sentences
        in the queryset. Mirrors the
        instance method.
        """
        user = get_user()
        sents = list(self.all())
        logs = []
        Log = get_model('pytoeba', 'Log')
        LocalizedTag = get_model('pytoeba', 'LocalizedTag')
        SentenceTag = get_model('pytoeba', 'SentenceTag')

        loctag = LocalizedTag.objects.get(text=text)
        sentags = list(SentenceTag.objects.filter(
            sentence__in=sents, tag_id=loctag.tag_id
            ))

        tag_hash_id = loctag.tag.hash_id
        for sent in sents:
            logs.append(
                Log(
                    sentence=sent, type='trd', done_by=user,
                    source_hash_id=sent.hash_id, source_lang=sent.lang,
                    target_id=loctag.tag_id, target_hash_id=tag_hash_id
                    )
                )

        bulk_delete(sentags)
        bulk_create(logs)


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

    def correct(self, sent_id, text, reason=''):
        sent = self.show(sent_id)
        sent.correct(text, reason)

    def accept_correction(self, sent_id, corr_id):
        sent = self.show(sent_id)
        sent.accept_correction(corr_id)

    def reject_correction(self, sent_id, corr_id):
        sent = self.show(sent_id)
        sent.reject_correction(corr_id)

    def force_correction(self, sent_id, corr_id):
        sent = self.show(sent_id)
        sent.force_correction(corr_id)

    def auto_force_correction(self, sent_id):
        sent = self.show(sent_id)
        sent.auto_force_correction()

    def add_tag(self, sent_id, text):
        sent = self.show(sent_id)
        sent.add_tag(text)

    def add_new_tag(self, sent_id, text, lang):
        sent = self.show(sent_id)
        sent.add_new_tag(text)

    def delete_tag(self, sent_id, text):
        sent = self.show(sent_id)
        sent.delete_tag(text)


class CorrectionQuerySet(QuerySet):

    def delete(self):
        for corr in self.all():
            corr.delete()

    def accept(self):
        for corr in self.all():
            corr.accept()

    def reject(self):
        for corr in self.all():
            corr.reject()

    def force(self):
        for corr in self.all():
            corr.force()


class CorrectionManager(Manager):

    def get_query_set(self):
        return CorrectionQuerySet(self.model, using=self._db)

    def add_to_obj(self, sent, text, reason=''):
        user = get_user()
        corr = self.create(
            sentence=sent, text=text, added_by=user, reason=reason
            )
        Log = get_model('pytoeba', 'Log')
        Log.objects.create(
            sentence=sent, type='cad', done_by=user, change_set=corr.text,
            target_id=corr.hash_id
            )
        return corr

    def add(self, sent_id, text, reason=''):
        Sentence = get_model('pytoeba', 'Sentence')
        sent = Sentence.objects.show(sent_id)
        corr = self.add_to_obj(sent, text, reason)
        return corr

    def edit(self, corr_id, text):
        corr = self.get(hash_id=corr_id)
        corr.edit(text)

    def delete(self, corr_id):
        corr = self.get(hash_id=corr_id)
        corr.delete()

    def accept(self, corr_id):
        corr = self.get(hash_id=corr_id)
        corr.accept()

    def reject(self, corr_id):
        corr = self.get(hash_id=corr_id)
        corr.reject()

    def force(self, corr_id):
        corr = self.get(hash_id=corr_id)
        corr.force()

    def auto_force(self, sent_id):
        sent = Sentence.objects.show(sent_id)
        sent.auto_force_correction()


class TagManager(Manager):

    def get_localization(self, tag_id, lang):
        tag = self.get(hash_id=tag_id)
        tag.get_localization(lang)

    def get_all_localizations(self, tag_id):
        tag = self.get(hash_id=tag_id)
        tag.get_all_localizations()

    def merge(self, source_id, target_id):
        source = self.get(hash_id=source_id)
        target = self.get(hash_id=target_id)
        source.merge(target)

    def translate(self, tag_id, text, lang):
        tag = self.get(hash_id=tag_id)
        tag.translate(text, lang)

    def add_new(self, text, lang):
        user = get_user()
        tag = self.create(added_by=user)
        tag.translate(text, lang)
        return tag


class PytoebaUserManager(UserManager):

    def _create_user(self, username, email, password,
                     is_staff, is_superuser, **extra_fields):
        """
        Overrides default _create_user in django's auth package.
        This is used by create_user and create_superuser on the
        default manager.
        """
        _now = now()
        if not username:
            raise ValueError('The given username must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email,
                          is_staff=is_staff, is_active=False,
                          is_superuser=is_superuser, last_login=_now,
                          date_joined=_now, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def _verify_status_obj(self, user, status='t'):
        if user.status == status:
            return True
        if user.status != status and \
        user.with_status_vote >= REQUIRED_STATUS_VOTES:
            user.status = status
            user.with_status_votes = 0
            user.against_status_votes = 0
            user.save(update_fields=[
                'status', 'with_status_votes', 'against_status_votes'
                ])
            return True
        return False

    def verify_status(self, username, status='t'):
        user = self.get(username=username)
        return self._verify_status_obj(user, status)

    def authenticate(username, password):
        return authenticate(username, password)

    def delete_expired_users(self):
        """
        Checks for expired users and deletes them.
        Returns a list containing the deleted users.
        """
        deleted_users = []
        for user in self.filter(is_staff=False, is_active=False):
            if user.userena_signup.activation_key_expired():
                deleted_users.append(user)
                user.delete()
        return deleted_users

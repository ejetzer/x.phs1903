# Source - https://stackoverflow.com/a/76453871
# Posted by sam2426679
# Retrieved 2026-08-14, License - CC BY-SA 4.0


class staticproperty(property):
    def __get__(self, owner_self, owner_cls):
        return self.fget()


class classproperty(property):
    def __get__(self, owner_self, owner_cls):
        return self.fget(owner_cls)

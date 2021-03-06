from pyramid.interfaces import IAuthorizationPolicy
from pyramid.interfaces import IAuthenticationPolicy
from pyramid.interfaces import IDefaultPermission

from pyramid.authorization import ACLAuthorizationPolicy
from pyramid.exceptions import ConfigurationError
from pyramid.config.util import action_method

class SecurityConfiguratorMixin(object):
    @action_method
    def set_authentication_policy(self, policy):
        """ Override the :app:`Pyramid` :term:`authentication policy` in the
        current configuration.  The ``policy`` argument must be an instance
        of an authentication policy or a :term:`dotted Python name`
        that points at an instance of an authentication policy.
        """
        self._set_authentication_policy(policy)
        def ensure():
            if self.autocommit:
                return
            if self.registry.queryUtility(IAuthorizationPolicy) is None:
                raise ConfigurationError(
                    'Cannot configure an authentication policy without '
                    'also configuring an authorization policy '
                    '(see the set_authorization_policy method)')
        self.action(IAuthenticationPolicy, callable=ensure)

    @action_method
    def _set_authentication_policy(self, policy):
        policy = self.maybe_dotted(policy)
        self.registry.registerUtility(policy, IAuthenticationPolicy)

    @action_method
    def set_authorization_policy(self, policy):
        """ Override the :app:`Pyramid` :term:`authorization policy` in the
        current configuration.  The ``policy`` argument must be an instance
        of an authorization policy or a :term:`dotted Python name` that points
        at an instance of an authorization policy.
        """
        self._set_authorization_policy(policy)
        def ensure():
            if self.registry.queryUtility(IAuthenticationPolicy) is None:
                raise ConfigurationError(
                    'Cannot configure an authorization policy without also '
                    'configuring an authentication policy '
                    '(see the set_authentication_policy method)')
        self.action(IAuthorizationPolicy, callable=ensure)

    @action_method
    def _set_authorization_policy(self, policy):
        policy = self.maybe_dotted(policy)
        self.registry.registerUtility(policy, IAuthorizationPolicy)

    @action_method
    def _set_security_policies(self, authentication, authorization=None):
        if (authorization is not None) and (not authentication):
            raise ConfigurationError(
                'If the "authorization" is passed a value, '
                'the "authentication" argument must also be '
                'passed a value; authorization requires authentication.')
        if authorization is None:
            authorization = ACLAuthorizationPolicy() # default
        self._set_authentication_policy(authentication)
        self._set_authorization_policy(authorization)

    @action_method
    def set_default_permission(self, permission):
        """
        Set the default permission to be used by all subsequent
        :term:`view configuration` registrations.  ``permission``
        should be a :term:`permission` string to be used as the
        default permission.  An example of a permission
        string:``'view'``.  Adding a default permission makes it
        unnecessary to protect each view configuration with an
        explicit permission, unless your application policy requires
        some exception for a particular view.

        If a default permission is *not* set, views represented by
        view configuration registrations which do not explicitly
        declare a permission will be executable by entirely anonymous
        users (any authorization policy is ignored).

        Later calls to this method override will conflict with earlier calls;
        there can be only one default permission active at a time within an
        application.

        .. warning::

          If a default permission is in effect, view configurations meant to
          create a truly anonymously accessible view (even :term:`exception
          view` views) *must* use the explicit permission string
          :data:`pyramid.security.NO_PERMISSION_REQUIRED` as the permission.
          When this string is used as the ``permission`` for a view
          configuration, the default permission is ignored, and the view is
          registered, making it available to all callers regardless of their
          credentials.

        See also :ref:`setting_a_default_permission`.

        .. note:: Using the ``default_permission`` argument to the
           :class:`pyramid.config.Configurator` constructor
           can be used to achieve the same purpose.
        """
        # default permission used during view registration
        self.registry.registerUtility(permission, IDefaultPermission)
        self.action(IDefaultPermission, None)



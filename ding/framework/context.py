from typing import Callable, List, Union
import pydash


class Context(dict):
    """
    Overview:
        Context is an object that pass contextual data between middlewares, whose life cycle is only one step.
        It is a dict that reflect itself, so you can set any properties as you wish.
    """

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.__dict__ = self
        self.total_step = 0  # Total steps
        self.step = 0  # Step in current episode
        self.episode = 0  # Total episodes
        self.state = None  # State received from env
        self.next_state = None  # Next state from env
        self.action = None  # Action
        self.reward = None  # Reward
        self.done = False  # Whether current step is the last step of current episode
        self.policy_output = None  # Policy output

        # Reserved properties
        self._backward_stack = []
        self._finish = False
        self._hooks_after_renew = [lambda new_, old: new_.update({"_finish": old._finish})]

    def renew(self) -> 'Context':  # noqa
        """
        Overview:
            Renew context from self, add total_step and shift kept properties to the new instance.
        """
        ctx = Context(total_step=self.total_step + 1)
        for hook in self._hooks_after_renew:
            hook(ctx, self)
        return ctx

    def keep(self, *keys: str) -> None:
        """
        Overview:
            Keep this key/keys until next iteration.
        """
        self.after_renew(lambda new_, old: new_.update(pydash.pick(old, keys)))

    def after_renew(self, fn: Callable) -> None:
        """
        Overview:
            Hook after renew, the function should look like (lambda new_, old: ...)
        Arguments:
            - fn (:obj:`Callable`): Hook after renew
        """
        self._hooks_after_renew.append(fn)

    def finish(self, finish: bool = True) -> None:
        """
        Overview:
            Set finish flag on context
        Arguments:
            - finish (:obj:`bool`): Finish or not
        """
        self._finish = finish

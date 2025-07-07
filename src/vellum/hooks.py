from typing import Callable, Dict, List, Literal, Type, Coroutine, Any

HookEvent = Literal["before_insert", "after_insert", "before_update", "after_update", "before_delete", "after_delete"]
HookFn = Callable[..., Coroutine[Any, Any, None]]
_HOOKS: Dict[Type, Dict[HookEvent, List[HookFn]]] = {} # type: ignore

def _register_hook(model_cls: Type, event: HookEvent, func: HookFn): # type: ignore
    if model_cls not in _HOOKS:
        _HOOKS[model_cls] = {
            "before_insert": [], "after_insert": [],
            "before_update": [], "after_update": [],
            "before_delete": [], "after_delete": [],
        }
    _HOOKS[model_cls][event].append(func)

def before_insert(func: HookFn) -> HookFn:
    setattr(func, '_vellum_hook_event', 'before_insert')
    return func

def after_insert(func: HookFn) -> HookFn:
    setattr(func, '_vellum_hook_event', 'after_insert')
    return func

def before_update(func: HookFn) -> HookFn:
    setattr(func, '_vellum_hook_event', 'before_update')
    return func

def after_update(func: HookFn) -> HookFn:
    setattr(func, '_vellum_hook_event', 'after_update')
    return func

def before_delete(func: HookFn) -> HookFn:
    setattr(func, '_vellum_hook_event', 'before_delete')
    return func

def after_delete(func: HookFn) -> HookFn:
    setattr(func, '_vellum_hook_event', 'after_delete')
    return func

def get_hooks_for_model(model_cls: Type, event: HookEvent) -> List[HookFn]: # type: ignore
    return _HOOKS.get(model_cls, {}).get(event, []) # type: ignore
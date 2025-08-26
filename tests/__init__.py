# Tests package for PrepAI

# Import all test modules for easy discovery
# Handle import errors gracefully in case dependencies are missing
test_modules = []

try:
    from . import test_api_integration
    test_modules.append('test_api_integration')
except ImportError:
    pass

try:
    from . import test_evaluation
    test_modules.append('test_evaluation')
except ImportError:
    pass

try:
    from . import test_interview_manager
    test_modules.append('test_interview_manager')
except ImportError:
    pass

try:
    from . import test_new_architecture
    test_modules.append('test_new_architecture')
except ImportError:
    pass

try:
    from . import test_phase1
    test_modules.append('test_phase1')
except ImportError:
    pass

try:
    from . import test_phase2
    test_modules.append('test_phase2')
except ImportError:
    pass

try:
    from . import test_phase2_enhanced
    test_modules.append('test_phase2_enhanced')
except ImportError:
    pass

try:
    from . import test_persona_variety
    test_modules.append('test_persona_variety')
except ImportError:
    pass

try:
    from . import test_unified_persona
    test_modules.append('test_unified_persona')
except ImportError:
    pass

try:
    from . import test_render_deployment
    test_modules.append('test_render_deployment')
except ImportError:
    pass

__all__ = test_modules

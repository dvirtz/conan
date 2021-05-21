import jinja2
from jinja2 import Template

from conans.errors import ConanException


class CMakeDepsFileTemplate(object):

    def __init__(self, cmakedeps, req):
        self.cmakedeps = cmakedeps
        if req is not None:
            self.conanfile = req
            self.pkg_name = req.ref.name
            self.package_folder = req.package_folder.\
                replace('\\', '/').replace('$', '\\$').replace('"', '\\"')
            self.target_namespace = get_target_namespace(self.conanfile)
            self.file_name = get_file_name(self.conanfile)

    def render(self):
        context = self.context
        if context is None:
            return
        return Template(self.template, trim_blocks=True, lstrip_blocks=True,
                        undefined=jinja2.StrictUndefined).render(context)

    def context(self):
        raise NotImplementedError()

    @property
    def template(self):
        raise NotImplementedError()

    @property
    def filename(self):
        raise NotImplementedError()

    @property
    def config_suffix(self):
        return "_{}".format(self.cmakedeps.configuration.upper()) \
            if self.cmakedeps.configuration else ""

    def get_target_namespace(self):
        return get_target_namespace(self.conanfile)

    def get_file_name(self):
        return get_file_name(self.conanfile)


def get_target_namespace(req):
    ret = req.new_cpp_info.get_property("cmake_target_name", "CMakeDeps")
    if not ret:
        ret = req.cpp_info.get_name("cmake_find_package_multi", default_name=False)
    return ret or req.ref.name


def get_file_name(req):
    ret = req.new_cpp_info.get_property("cmake_file_name", "CMakeDeps")
    if not ret:
        ret = req.cpp_info.get_filename("cmake_find_package_multi", default_name=False)
    return ret or req.ref.name


def get_component_alias(req, comp_name):
    if comp_name not in req.new_cpp_info.components:
        # foo::foo might be referencing the root cppinfo
        if req.ref.name == comp_name:
            return comp_name
        raise ConanException("Component '{name}::{cname}' not found in '{name}' "
                             "package requirement".format(name=req.ref.name, cname=comp_name))
    ret = req.new_cpp_info.components[comp_name].get_property("cmake_target_name", "CMakeDeps")
    if not ret:
        ret = req.cpp_info.components[comp_name].get_name("cmake_find_package_multi",
                                                          default_name=False)
    return ret or comp_name
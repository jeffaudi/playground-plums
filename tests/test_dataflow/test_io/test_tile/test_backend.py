import sys
import contextlib
import unittest.mock as mock

import pytest
import numpy as np

from playground_plums.commons.path import Path


@pytest.fixture(params=('ext', 'no_ext'))
def jpeg_image(request):
    if request.param == 'no_ext':
        return Path(__file__)[:-1] / '_data' / 'test_jpg'
    return Path(__file__)[:-1] / '_data' / 'test_jpg.jpg'


@pytest.fixture(params=('ext', 'no_ext'))
def png_image(request):
    if request.param == 'no_ext':
        return Path(__file__)[:-1] / '_data' / 'test_png'
    return Path(__file__)[:-1] / '_data' / 'test_png.png'


@pytest.fixture(params=('jpg', 'png'))
def image(request, png_image, jpeg_image):
    if request.param == 'jpg':
        return jpeg_image
    return png_image


@pytest.fixture(params=('jpg', 'png'))
def image_ext(request):
    if request.param == 'jpg':
        return Path(__file__)[:-1] / '_data' / 'test_jpg.jpg'
    return Path(__file__)[:-1] / '_data' / 'test_png.png'


@pytest.fixture(params=('jpg', 'png'))
def image_no_ext(request):
    if request.param == 'jpg':
        return Path(__file__)[:-1] / '_data' / 'test_jpg'
    return Path(__file__)[:-1] / '_data' / 'test_png'


@contextlib.contextmanager
def disable_import(*modules):
    with mock.patch.dict(sys.modules, {mod: None for mod in modules}) as context:
        yield [context]


def psnr(reference_image, test_image):
    """Compute the :math:`PSNR` between two image stored as uint8 HWC :class:`numpy.ndarray`.

    Args:
        reference_image (numpy.ndarray): The reference image as a uint8 HWC :class:`numpy.ndarray`.
        test_image (numpy.ndarray): The reference image as a uint8 HWC :class:`numpy.ndarray`.

    Returns:
        float: The computed :math:`PSNR` between the two images.

    """
    return 20 * np.log10(255) - 10 * np.log10(np.mean((reference_image - test_image)**2))


class TestImport:
    @pytest.fixture(autouse=True)
    def clean_up(self):
        # Ugly cleanup
        for module in [module for module in sys.modules if 'playground_plums.dataflow.io.tile._backend' in module]:
            try:
                del sys.modules[module]
            except KeyError:
                pass
        try:
            del sys.modules['PIL']
        except KeyError:
            pass
        try:
            del sys.modules['PIL.Image']
        except KeyError:
            pass
        try:
            del sys.modules['lycon']
        except KeyError:
            pass
        try:
            del sys.modules['cv2']
        except KeyError:
            pass

        yield

    def test_all_fail(self):
        with pytest.raises(ImportError, match='Error importing playground_plums.dataflow.io: '
                                              'No suitable image backend where found. '
                                              'For more information, please refer to the documentation.'):
            with disable_import('PIL', 'lycon', 'cv2', 'playground_plums.dataflow.io.tile._vendor.turbojpeg'):
                import playground_plums.dataflow.io.tile._backend  # noqa: F401

    def test_pillow_fail(self):
        with disable_import('PIL'):
            import playground_plums.dataflow.io.tile._backend
            assert not playground_plums.dataflow.io.tile._backend._HAS_PILLOW
            assert playground_plums.dataflow.io.tile._backend._HAS_LYCON
            assert playground_plums.dataflow.io.tile._backend._HAS_CV2
            assert playground_plums.dataflow.io.tile._backend._HAS_TURBO_JPEG

    def test_lycon_fail(self):
        with disable_import('lycon'):
            import playground_plums.dataflow.io.tile._backend
            assert playground_plums.dataflow.io.tile._backend._HAS_PILLOW
            assert not playground_plums.dataflow.io.tile._backend._HAS_LYCON
            assert playground_plums.dataflow.io.tile._backend._HAS_CV2
            assert playground_plums.dataflow.io.tile._backend._HAS_TURBO_JPEG

    def test_onpen_cv_fail(self):
        with disable_import('cv2'):
            import playground_plums.dataflow.io.tile._backend
            assert playground_plums.dataflow.io.tile._backend._HAS_PILLOW
            assert playground_plums.dataflow.io.tile._backend._HAS_LYCON
            assert not playground_plums.dataflow.io.tile._backend._HAS_CV2
            assert playground_plums.dataflow.io.tile._backend._HAS_TURBO_JPEG

    def test_turbo_jpeg_fail(self):
        with disable_import('playground_plums.dataflow.io.tile._vendor.turbojpeg'):
            import playground_plums.dataflow.io.tile._backend
            assert playground_plums.dataflow.io.tile._backend._HAS_PILLOW
            assert playground_plums.dataflow.io.tile._backend._HAS_LYCON
            assert playground_plums.dataflow.io.tile._backend._HAS_CV2
            assert not playground_plums.dataflow.io.tile._backend._HAS_TURBO_JPEG


class TestLoad:
    @pytest.fixture(autouse=True)
    def clean_up(self):
        # Ugly cleanup
        for module in [module for module in sys.modules if 'playground_plums.dataflow.io.tile._backend' in module]:
            try:
                del sys.modules[module]
            except KeyError:
                pass
        try:
            del sys.modules['PIL']
        except KeyError:
            pass
        try:
            del sys.modules['PIL.Image']
        except KeyError:
            pass
        try:
            del sys.modules['lycon']
        except KeyError:
            pass
        try:
            del sys.modules['cv2']
        except KeyError:
            pass

        yield

    @pytest.mark.parametrize('disabled_backend', (('none', ), ('playground_plums.dataflow.io.tile._vendor.turbojpeg', ),
                                                  ('playground_plums.dataflow.io.tile._vendor.turbojpeg', 'lycon'),
                                                  ('playground_plums.dataflow.io.tile._vendor.turbojpeg', 'lycon',
                                                   'cv2'),
                                                  ('lycon', 'cv2'),
                                                  ('playground_plums.dataflow.io.tile._vendor.turbojpeg', 'cv2'),
                                                  ('playground_plums.dataflow.io.tile._vendor.turbojpeg', 'lycon',
                                                   'PIL'),
                                                  ('playground_plums.dataflow.io.tile._vendor.turbojpeg', 'PIL'),
                                                  ('lycon', 'cv2', 'PIL'),
                                                  ('lycon', 'PIL'),
                                                  ('cv2', 'PIL')), ids=lambda backends: ', '.join(backends))
    def test_jpeg_ext(self, disabled_backend):
        with disable_import(*disabled_backend):
            from playground_plums.dataflow.io.tile._backend import _load_jpg
            array = _load_jpg(Path(__file__)[:-1] / '_data/test_jpg.jpg')
            array_noext = _load_jpg(Path(__file__)[:-1] / '_data/test_jpg')

            assert np.array_equal(array, array_noext)

    def test_jpeg_no_backend(self):
        with disable_import('playground_plums.dataflow.io.tile._vendor.turbojpeg', 'lycon', 'cv2'):
            import playground_plums.dataflow.io.tile._backend
            # Disable Pillow after import to avoid early raise
            playground_plums.dataflow.io.tile._backend._HAS_PILLOW = False

            with pytest.raises(RuntimeError, match='No backend available to open JPG image.'):
                playground_plums.dataflow.io.tile._backend._load_jpg(Path(__file__)[:-1] / '_data/test_jpg.jpg')

            with pytest.raises(RuntimeError, match='No backend available to open JPG image.'):
                playground_plums.dataflow.io.tile._backend._load_jpg(Path(__file__)[:-1] / '_data/test_jpg')

    @pytest.mark.parametrize('disabled_backend', (('none', ), ('playground_plums.dataflow.io.tile._vendor.turbojpeg', ),
                                                  ('playground_plums.dataflow.io.tile._vendor.turbojpeg', 'lycon'),
                                                  ('playground_plums.dataflow.io.tile._vendor.turbojpeg', 'lycon',
                                                   'cv2'),
                                                  ('lycon', 'cv2'),
                                                  ('playground_plums.dataflow.io.tile._vendor.turbojpeg', 'cv2'),
                                                  ('playground_plums.dataflow.io.tile._vendor.turbojpeg', 'lycon',
                                                   'PIL'),
                                                  ('playground_plums.dataflow.io.tile._vendor.turbojpeg', 'PIL'),
                                                  ('lycon', 'PIL'),
                                                  ('cv2', 'PIL')), ids=lambda backends: ', '.join(backends))
    def test_png_ext(self, disabled_backend):
        with disable_import(*disabled_backend):
            from playground_plums.dataflow.io.tile._backend import _load_png
            array = _load_png(Path(__file__)[:-1] / '_data/test_png.png')
            array_noext = _load_png(Path(__file__)[:-1] / '_data/test_png')

            assert np.array_equal(array, array_noext)

    def test_png_no_backend(self):
        with disable_import('lycon', 'cv2', 'PIL'):
            import playground_plums.dataflow.io.tile._backend
            with pytest.raises(RuntimeError, match='No backend available to open PNG image.'):
                playground_plums.dataflow.io.tile._backend._load_png(Path(__file__)[:-1] / '_data/test_png.png')

            with pytest.raises(RuntimeError, match='No backend available to open PNG image.'):
                playground_plums.dataflow.io.tile._backend._load_png(Path(__file__)[:-1] / '_data/test_png')

    @pytest.mark.parametrize('disabled_backend', (('none', ), ('playground_plums.dataflow.io.tile._vendor.turbojpeg', ),
                                                  ('playground_plums.dataflow.io.tile._vendor.turbojpeg', 'lycon'),
                                                  ('playground_plums.dataflow.io.tile._vendor.turbojpeg', 'lycon',
                                                   'cv2'),
                                                  ('lycon', 'cv2'),
                                                  ('playground_plums.dataflow.io.tile._vendor.turbojpeg', 'cv2'),
                                                  ('playground_plums.dataflow.io.tile._vendor.turbojpeg', 'lycon',
                                                   'PIL'),
                                                  ('playground_plums.dataflow.io.tile._vendor.turbojpeg', 'PIL'),
                                                  ('lycon', 'PIL'),
                                                  ('cv2', 'PIL')), ids=lambda backends: ', '.join(backends))
    def test_png_jpg(self, disabled_backend):
        with disable_import(*disabled_backend):
            from playground_plums.dataflow.io.tile._backend import _load_png, _load_jpg
            array_png = _load_png(Path(__file__)[:-1] / '_data/test_png.png').astype(np.float64)
            array_noext_png = _load_png(Path(__file__)[:-1] / '_data/test_png').astype(np.float64)
            array_jpg = _load_jpg(Path(__file__)[:-1] / '_data/test_jpg.jpg').astype(np.float64)
            array_noext_jpg = _load_jpg(Path(__file__)[:-1] / '_data/test_jpg').astype(np.float64)

            assert psnr(array_jpg, array_png) > 35
            assert psnr(array_jpg, array_noext_png) > 35
            assert psnr(array_noext_jpg, array_png) > 35
            assert psnr(array_noext_jpg, array_noext_png) > 35


class TestDump:
    @pytest.fixture(autouse=True)
    def clean_up(self):
        # Ugly cleanup
        for module in [module for module in sys.modules if 'playground_plums.dataflow.io.tile._backend' in module]:
            try:
                del sys.modules[module]
            except KeyError:
                pass
        try:
            del sys.modules['PIL']
        except KeyError:
            pass
        try:
            del sys.modules['PIL.Image']
        except KeyError:
            pass
        try:
            del sys.modules['lycon']
        except KeyError:
            pass
        try:
            del sys.modules['cv2']
        except KeyError:
            pass

        yield

    @pytest.mark.parametrize('disabled_backend', (('none', ), ('playground_plums.dataflow.io.tile._vendor.turbojpeg', ),
                                                  ('playground_plums.dataflow.io.tile._vendor.turbojpeg', 'lycon'),
                                                  ('playground_plums.dataflow.io.tile._vendor.turbojpeg', 'lycon',
                                                   'cv2'),
                                                  ('lycon', 'cv2'),
                                                  ('playground_plums.dataflow.io.tile._vendor.turbojpeg', 'cv2'),
                                                  ('playground_plums.dataflow.io.tile._vendor.turbojpeg', 'lycon',
                                                   'PIL'),
                                                  ('playground_plums.dataflow.io.tile._vendor.turbojpeg', 'PIL'),
                                                  ('lycon', 'cv2', 'PIL'),
                                                  ('lycon', 'PIL'),
                                                  ('cv2', 'PIL')), ids=lambda backends: ', '.join(backends))
    def test_dump_jpg(self, disabled_backend, jpeg_image, tmp_path):
        image_path = tmp_path / 'test.jpg'
        with disable_import(*disabled_backend):
            from playground_plums.dataflow.io.tile._backend import _dump_jpg, _load_jpg
            loaded = _load_jpg(jpeg_image)
            _dump_jpg(image_path, loaded)
            reloaded = _load_jpg(image_path)
            assert psnr(loaded.astype(np.float64), reloaded.astype(np.float64)) > 31

    @pytest.mark.parametrize('disabled_backend', (('none',), ('playground_plums.dataflow.io.tile._vendor.turbojpeg',),
                                                  ('playground_plums.dataflow.io.tile._vendor.turbojpeg', 'lycon'),
                                                  ('playground_plums.dataflow.io.tile._vendor.turbojpeg', 'lycon',
                                                   'cv2'),
                                                  ('lycon', 'cv2'),
                                                  ('playground_plums.dataflow.io.tile._vendor.turbojpeg', 'cv2'),
                                                  ('playground_plums.dataflow.io.tile._vendor.turbojpeg', 'lycon',
                                                   'PIL'),
                                                  ('playground_plums.dataflow.io.tile._vendor.turbojpeg', 'PIL'),
                                                  ('lycon', 'PIL'),
                                                  ('cv2', 'PIL')), ids=lambda backends: ', '.join(backends))
    def test_dump_png(self, disabled_backend, jpeg_image, tmp_path):
        image_path = tmp_path / 'test.png'
        with disable_import(*disabled_backend):
            from playground_plums.dataflow.io.tile._backend import _dump_png, _load_png
            loaded = _load_png(jpeg_image)
            _dump_png(image_path, loaded)
            reloaded = _load_png(image_path)
            assert psnr(loaded.astype(np.float64), reloaded.astype(np.float64)) > 35


class TestImage:
    @pytest.fixture(autouse=True)
    def clean_up(self):
        # Ugly cleanup
        for module in [module for module in sys.modules if 'playground_plums.dataflow.io.tile._backend' in module]:
            try:
                del sys.modules[module]
            except KeyError:
                pass
        try:
            del sys.modules['PIL']
        except KeyError:
            pass
        try:
            del sys.modules['PIL.Image']
        except KeyError:
            pass
        try:
            del sys.modules['lycon']
        except KeyError:
            pass
        try:
            del sys.modules['cv2']
        except KeyError:
            pass

        yield

    @pytest.mark.parametrize('disabled_backend', (('none',), ('playground_plums.dataflow.io.tile._vendor.turbojpeg',),
                                                  ('playground_plums.dataflow.io.tile._vendor.turbojpeg', 'lycon'),
                                                  ('playground_plums.dataflow.io.tile._vendor.turbojpeg', 'lycon',
                                                   'cv2'),
                                                  ('lycon', 'cv2'),
                                                  ('playground_plums.dataflow.io.tile._vendor.turbojpeg', 'cv2'),
                                                  ('playground_plums.dataflow.io.tile._vendor.turbojpeg', 'lycon',
                                                   'PIL'),
                                                  ('playground_plums.dataflow.io.tile._vendor.turbojpeg', 'PIL'),
                                                  ('lycon', 'PIL'),
                                                  ('cv2', 'PIL')), ids=lambda backends: ', '.join(backends))
    def test_load(self, disabled_backend, image):
        with disable_import(*disabled_backend):
            from playground_plums.dataflow.io.tile._backend import Image, _load_jpg, _load_png
            load = _load_png if 'png' in str(image) else _load_jpg
            assert np.array_equal(Image.load(image)._array_data, load(image))

    @pytest.mark.parametrize('disabled_backend', (('none',), ('playground_plums.dataflow.io.tile._vendor.turbojpeg',),
                                                  ('playground_plums.dataflow.io.tile._vendor.turbojpeg', 'lycon'),
                                                  ('playground_plums.dataflow.io.tile._vendor.turbojpeg', 'lycon',
                                                   'cv2'),
                                                  ('lycon', 'cv2'),
                                                  ('playground_plums.dataflow.io.tile._vendor.turbojpeg', 'cv2'),
                                                  ('playground_plums.dataflow.io.tile._vendor.turbojpeg', 'lycon',
                                                   'PIL'),
                                                  ('playground_plums.dataflow.io.tile._vendor.turbojpeg', 'PIL'),
                                                  ('lycon', 'PIL'),
                                                  ('cv2', 'PIL')), ids=lambda backends: ', '.join(backends))
    def test_dump_ext_input(self, disabled_backend, image_ext, tmp_path):
        image_path = tmp_path / ('test' + image_ext.ext)
        with disable_import(*disabled_backend):
            from playground_plums.dataflow.io.tile._backend import Image
            Image.load(image_ext).save(image_path)
            assert psnr(Image.load(image_ext)._array_data, Image.load(image_path)._array_data) > 35

    @pytest.mark.parametrize('disabled_backend', (('none',), ('playground_plums.dataflow.io.tile._vendor.turbojpeg',),
                                                  ('playground_plums.dataflow.io.tile._vendor.turbojpeg', 'lycon'),
                                                  ('playground_plums.dataflow.io.tile._vendor.turbojpeg', 'lycon',
                                                   'cv2'),
                                                  ('lycon', 'cv2'),
                                                  ('playground_plums.dataflow.io.tile._vendor.turbojpeg', 'cv2'),
                                                  ('playground_plums.dataflow.io.tile._vendor.turbojpeg', 'lycon',
                                                   'PIL'),
                                                  ('playground_plums.dataflow.io.tile._vendor.turbojpeg', 'PIL'),
                                                  ('lycon', 'PIL'),
                                                  ('cv2', 'PIL')), ids=lambda backends: ', '.join(backends))
    def test_dump_no_ext_input(self, disabled_backend, image_no_ext, tmp_path):
        image_path = tmp_path / ('test' + '.jpg')
        with disable_import(*disabled_backend):
            from playground_plums.dataflow.io.tile._backend import Image
            Image.load(image_no_ext).save(image_path)
            assert psnr(Image.load(image_no_ext)._array_data, Image.load(image_path)._array_data) > 34

        image_path = tmp_path / ('test' + '.png')
        with disable_import(*disabled_backend):
            from playground_plums.dataflow.io.tile._backend import Image
            Image.load(image_no_ext).save(image_path)
            assert psnr(Image.load(image_no_ext)._array_data, Image.load(image_path)._array_data) > 34

    @pytest.mark.parametrize('disabled_backend', (('none',), ('playground_plums.dataflow.io.tile._vendor.turbojpeg',),
                                                  ('playground_plums.dataflow.io.tile._vendor.turbojpeg', 'lycon'),
                                                  ('playground_plums.dataflow.io.tile._vendor.turbojpeg', 'lycon',
                                                   'cv2'),
                                                  ('lycon', 'cv2'),
                                                  ('playground_plums.dataflow.io.tile._vendor.turbojpeg', 'cv2'),
                                                  ('playground_plums.dataflow.io.tile._vendor.turbojpeg', 'lycon',
                                                   'PIL'),
                                                  ('playground_plums.dataflow.io.tile._vendor.turbojpeg', 'PIL'),
                                                  ('lycon', 'PIL'),
                                                  ('cv2', 'PIL')), ids=lambda backends: ', '.join(backends))
    def test_dump_no_ext(self, disabled_backend, image, tmp_path):
        image_path = tmp_path / 'test'
        with disable_import(*disabled_backend):
            from playground_plums.dataflow.io.tile._backend import Image
            with pytest.raises(ValueError, match='Unsupported image type'):
                Image.load(image).save(image_path)

import pytest
import numpy as np

from playground_plums.dataflow.io.tile._format.channels import Channel, channels_register, Red, Green, Blue, Grey, Alpha
from playground_plums.dataflow.io.tile._format import ptype, rgb, rgba, bgr, bgra, y


def make_channel(value):
    return value * np.ones((12, 12, 1), dtype=np.float64)


def make_image(n_channels):
    return np.concatenate([make_channel(i + 1) for i in range(n_channels)], axis=-1)


class TestChannel:
    @staticmethod
    def base_channel(channel):
        # Test for class registration
        assert channel.__short_name__ in channels_register
        assert channel.__short_name__.lower() in channels_register
        assert channel.__full_name__ in channels_register

        assert channels_register[channel.__short_name__] == channel
        assert channels_register[channel.__short_name__.lower()] == channel
        assert channels_register[channel.__full_name__] == channel

        # Test representation
        assert str(channel) == channel.__full_name__
        assert repr(channel) == 'Channel({})'.format(channel)
        assert hash(channel) == hash(str(channel))

        # Test equality
        assert channel == channel
        assert not channel != channel

        class DummyChannel(Channel):
            __short_name__ = 'D'
            __full_name__ = 'DUMMY'

        dummy = DummyChannel()
        assert not channel == dummy
        assert channel != dummy

        assert not channel == channel.__id__
        assert channel != channel.__id__

    def test_channel(self):
        channel = Channel()
        self.base_channel(channel)

        data = make_channel(2)
        assert np.array_equal(channel.get_conversion_fn_from(ptype('X'))(data), data[..., 0])
        assert np.array_equal(channel.get_conversion_fn_from(ptype('R'))(data), np.ones((12, 12), dtype=np.float64))

        data = make_image(4)
        assert np.array_equal(channel.get_conversion_fn_from(ptype('RBXG'))(data), data[..., 2])

    def test_red(self):
        channel = Red()
        self.base_channel(channel)

        data = make_channel(2)
        assert np.array_equal(channel.get_conversion_fn_from(ptype('R'))(data), data[..., 0])
        assert np.array_equal(channel.get_conversion_fn_from(ptype('X'))(data), np.ones((12, 12), dtype=np.float64))

        data = make_image(4)
        assert np.array_equal(channel.get_conversion_fn_from(ptype('XBRG'))(data), data[..., 2])

        data = make_image(1)
        assert np.array_equal(channel.get_conversion_fn_from(ptype('Y'))(data), data[..., 0])

    def test_green(self):
        channel = Green()
        self.base_channel(channel)

        data = make_channel(2)
        assert np.array_equal(channel.get_conversion_fn_from(ptype('G'))(data), data[..., 0])
        assert np.array_equal(channel.get_conversion_fn_from(ptype('X'))(data), np.ones((12, 12), dtype=np.float64))

        data = make_image(4)
        assert np.array_equal(channel.get_conversion_fn_from(ptype('XBGR'))(data), data[..., 2])

        data = make_image(1)
        assert np.array_equal(channel.get_conversion_fn_from(ptype('Y'))(data), data[..., 0])

    def test_blue(self):
        channel = Blue()
        self.base_channel(channel)

        data = make_channel(2)
        assert np.array_equal(channel.get_conversion_fn_from(ptype('B'))(data), data[..., 0])
        assert np.array_equal(channel.get_conversion_fn_from(ptype('X'))(data), np.ones((12, 12), dtype=np.float64))

        data = make_image(4)
        assert np.array_equal(channel.get_conversion_fn_from(ptype('XGBR'))(data), data[..., 2])

        data = make_image(1)
        assert np.array_equal(channel.get_conversion_fn_from(ptype('Y'))(data), data[..., 0])

    def test_grey(self):
        channel = Grey()
        self.base_channel(channel)

        data = make_channel(2)
        assert np.array_equal(channel.get_conversion_fn_from(ptype('Y'))(data), data[..., 0])
        assert np.array_equal(channel.get_conversion_fn_from(ptype('X'))(data), np.ones((12, 12), dtype=np.float64))

        data = make_image(4)
        assert np.array_equal(channel.get_conversion_fn_from(ptype('BGYR'))(data), data[..., 2])

        data = make_image(3)
        assert np.allclose(channel.get_conversion_fn_from(ptype('RGB'))(data), 1.815 * np.ones((12, 12)))
        assert np.allclose(channel.get_conversion_fn_from(ptype('BGR'))(data), 2.1849999999999996 * np.ones((12, 12)))
        assert np.allclose(channel.get_conversion_fn_from(ptype('GBR'))(data), 1.712 * np.ones((12, 12)))
        assert np.allclose(channel.get_conversion_fn_from(ptype('RBG'))(data), 2.2880000000000003 * np.ones((12, 12)))
        assert np.allclose(channel.get_conversion_fn_from(ptype('GRB'))(data), 1.5270000000000001 * np.ones((12, 12)))
        assert np.allclose(channel.get_conversion_fn_from(ptype('BRG'))(data), 2.473 * np.ones((12, 12)))

        data = make_image(4)
        assert np.allclose(channel.get_conversion_fn_from(ptype('RGBA'))(data), 1.815 * np.ones((12, 12)))
        assert np.allclose(channel.get_conversion_fn_from(ptype('BGRA'))(data), 2.1849999999999996 * np.ones((12, 12)))
        assert np.allclose(channel.get_conversion_fn_from(ptype('GBRA'))(data), 1.712 * np.ones((12, 12)))
        assert np.allclose(channel.get_conversion_fn_from(ptype('RBGA'))(data), 2.2880000000000003 * np.ones((12, 12)))
        assert np.allclose(channel.get_conversion_fn_from(ptype('GRBA'))(data), 1.5270000000000001 * np.ones((12, 12)))
        assert np.allclose(channel.get_conversion_fn_from(ptype('BRGA'))(data), 2.473 * np.ones((12, 12)))

    def test_alpha(self):
        channel = Alpha()
        self.base_channel(channel)

        data = make_channel(2)
        assert np.array_equal(channel.get_conversion_fn_from(ptype('A'))(data), data[..., 0])
        assert np.array_equal(channel.get_conversion_fn_from(ptype('X'))(data), np.ones((12, 12), dtype=np.float64))

        data = make_image(4)
        assert np.array_equal(channel.get_conversion_fn_from(ptype('BGAR'))(data), data[..., 2])


class TestPType:
    @staticmethod
    def base_channel(ptype, *channels):
        # Test for class creation
        assert ptype._channels == channels

        # Test representation
        assert str(ptype) == ''.join(channel.__short_name__ for channel in channels)
        assert repr(ptype) == 'ptype(\'{}\')'.format(ptype)
        assert hash(ptype) == hash(channels)

        # Test len and getitem
        assert len(ptype) == len(channels)
        assert tuple(ptype[i] for i in range(len(channels))) == channels
        assert tuple(channel for channel in ptype) == channels

        # Test equality
        assert ptype == ptype
        assert not ptype != ptype
        assert ptype == channels
        assert not ptype != channels
        if len(ptype) > 1:
            assert not ptype == channels[:2]
            assert ptype != channels[:2]
        assert not ptype == 0
        assert ptype != 0

        # Test slice and index
        class DummyChannel(Channel):
            __short_name__ = 'D'
            __full_name__ = 'DUMMY'

        dummy = DummyChannel()
        reversed_channels = tuple(reversed(channels))
        # +-> Slice
        assert ptype.slice(dummy) is None
        if len(ptype) > 1:
            assert ptype.slice(reversed_channels) is None
        assert ptype.slice(channels) == (0, len(channels))
        # +-> Index
        assert ptype.index(dummy) is None
        assert ptype.index(reversed_channels) == tuple(reversed(range(len(channels))))
        assert ptype.index(channels) == tuple(range(len(channels)))

    def test_rgb(self):
        channels = (Red(), Green(), Blue())
        self.base_channel(rgb, *channels)

    def test_rgba(self):
        channels = (Red(), Green(), Blue(), Alpha())
        self.base_channel(rgba, *channels)

    def test_bgr(self):
        channels = (Blue(), Green(), Red())
        self.base_channel(bgr, *channels)

    def test_bgra(self):
        channels = (Blue(), Green(), Red(), Alpha())
        self.base_channel(bgra, *channels)

    def test_grey(self):
        channels = (Grey(), )
        self.base_channel(y, *channels)

    def test_conversion_fn(self):  # noqa: R701
        # Test representation
        assert repr(rgb.get_conversion_fn_to(rgb)) == str(rgb.get_conversion_fn_to(rgb)) == 'RGBToRGB()'
        assert repr(rgb.get_conversion_fn_to(bgr)) == str(rgb.get_conversion_fn_to(bgr)) == 'RGBToBGR()'
        assert repr(rgb.get_conversion_fn_to(rgba)) == str(rgb.get_conversion_fn_to(rgba)) == 'RGBToRGBA()'
        assert repr(rgb.get_conversion_fn_to(bgra)) == str(rgb.get_conversion_fn_to(bgra)) == 'RGBToBGRA()'
        assert repr(rgb.get_conversion_fn_to(y)) == str(rgb.get_conversion_fn_to(y)) == 'RGBToY()'

        assert repr(bgr.get_conversion_fn_to(rgb)) == str(bgr.get_conversion_fn_to(rgb)) == 'BGRToRGB()'
        assert repr(bgr.get_conversion_fn_to(bgr)) == str(bgr.get_conversion_fn_to(bgr)) == 'BGRToBGR()'
        assert repr(bgr.get_conversion_fn_to(rgba)) == str(bgr.get_conversion_fn_to(rgba)) == 'BGRToRGBA()'
        assert repr(bgr.get_conversion_fn_to(bgra)) == str(bgr.get_conversion_fn_to(bgra)) == 'BGRToBGRA()'
        assert repr(bgr.get_conversion_fn_to(y)) == str(bgr.get_conversion_fn_to(y)) == 'BGRToY()'

        assert repr(rgba.get_conversion_fn_to(rgb)) == str(rgba.get_conversion_fn_to(rgb)) == 'RGBAToRGB()'
        assert repr(rgba.get_conversion_fn_to(bgr)) == str(rgba.get_conversion_fn_to(bgr)) == 'RGBAToBGR()'
        assert repr(rgba.get_conversion_fn_to(rgba)) == str(rgba.get_conversion_fn_to(rgba)) == 'RGBAToRGBA()'
        assert repr(rgba.get_conversion_fn_to(bgra)) == str(rgba.get_conversion_fn_to(bgra)) == 'RGBAToBGRA()'
        assert repr(rgba.get_conversion_fn_to(y)) == str(rgba.get_conversion_fn_to(y)) == 'RGBAToY()'

        assert repr(bgra.get_conversion_fn_to(rgb)) == str(bgra.get_conversion_fn_to(rgb)) == 'BGRAToRGB()'
        assert repr(bgra.get_conversion_fn_to(bgr)) == str(bgra.get_conversion_fn_to(bgr)) == 'BGRAToBGR()'
        assert repr(bgra.get_conversion_fn_to(rgba)) == str(bgra.get_conversion_fn_to(rgba)) == 'BGRAToRGBA()'
        assert repr(bgra.get_conversion_fn_to(bgra)) == str(bgra.get_conversion_fn_to(bgra)) == 'BGRAToBGRA()'
        assert repr(bgra.get_conversion_fn_to(y)) == str(bgra.get_conversion_fn_to(y)) == 'BGRAToY()'

        assert repr(y.get_conversion_fn_to(rgb)) == str(y.get_conversion_fn_to(rgb)) == 'YToRGB()'
        assert repr(y.get_conversion_fn_to(bgr)) == str(y.get_conversion_fn_to(bgr)) == 'YToBGR()'
        assert repr(y.get_conversion_fn_to(rgba)) == str(y.get_conversion_fn_to(rgba)) == 'YToRGBA()'
        assert repr(y.get_conversion_fn_to(bgra)) == str(y.get_conversion_fn_to(bgra)) == 'YToBGRA()'
        assert repr(y.get_conversion_fn_to(y)) == str(y.get_conversion_fn_to(y)) == 'YToY()'

        # Test sanity check
        with pytest.raises(ValueError, match=r'Inconsistent shape: Expected [0-9] channels but got [0-9]\.'):
            rgb.get_conversion_fn_to(rgb)(make_image(5))

        with pytest.raises(ValueError, match=r'Inconsistent shape: Expected [0-9] channels but got [0-9]\.'):
            rgb.get_conversion_fn_to(y)(make_image(1))

        with pytest.raises(ValueError, match=r'Inconsistent shape: Expected [0-9] channels but got [0-9]\.'):
            rgb.get_conversion_fn_to(rgba)(make_image(4))

        with pytest.raises(ValueError, match=r'Inconsistent shape: Expected [0-9] channels but got [0-9]\.'):
            rgba.get_conversion_fn_to(rgba)(make_image(5))

        with pytest.raises(ValueError, match=r'Inconsistent shape: Expected [0-9] channels but got [0-9]\.'):
            rgba.get_conversion_fn_to(y)(make_image(1))

        with pytest.raises(ValueError, match=r'Inconsistent shape: Expected [0-9] channels but got [0-9]\.'):
            rgba.get_conversion_fn_to(rgb)(make_image(3))

        with pytest.raises(ValueError, match=r'Inconsistent shape: Expected [0-9] channels but got [0-9]\.'):
            y.get_conversion_fn_to(y)(make_image(5))

        with pytest.raises(ValueError, match=r'Inconsistent shape: Expected [0-9] channels but got [0-9]\.'):
            y.get_conversion_fn_to(rgb)(make_image(3))

        with pytest.raises(ValueError, match=r'Inconsistent shape: Expected [0-9] channels but got [0-9]\.'):
            y.get_conversion_fn_to(rgba)(make_image(4))

    def test_conversions(self):  # noqa: R701
        # .....................................................................
        # :  /   : RGB       : BGR       : RGBA    : BGRA    : GREY           :
        # .....................................................................
        # : RGB  : Id        : Rev       : Id+New  : Rev+New : Comb           :
        # .....................................................................
        # : BGR  : Rev       : Id        : Rev+New : Id+New  : Rev+Comb       :
        # .....................................................................
        # : RGBA : Trunc     : Rev+Trunc : Id      : Rev+Id  : Comb+Trunc     :
        # .....................................................................
        # : BGRA : Rev+Trunc : Trunc     : Rev+Id  : Id      : Rev+Comb+Trunc :
        # .....................................................................
        # : GREY : Id*3      : Id*3      : Id+New  : Id+New  : Id             :
        # :......:...........:...........:.........:.........:................:

        # RGB:
        # +-> Row
        data = make_image(3)
        assert np.array_equal(rgb.get_conversion_fn_to(rgb)(data), data)
        assert np.array_equal(rgb.get_conversion_fn_to(bgr)(data), data[..., ::-1])
        assert np.array_equal(rgb.get_conversion_fn_to(rgba)(data), np.concatenate((data, make_channel(1)), axis=-1))
        assert np.array_equal(rgb.get_conversion_fn_to(bgra)(data), np.concatenate((data[..., ::-1],
                                                                                    make_channel(1)), axis=-1))
        assert np.array_equal(rgb.get_conversion_fn_to(y)(data), make_channel(1.815))
        # +-> Column
        data = make_image(3)
        assert np.array_equal(bgr.get_conversion_fn_to(rgb)(data), data[..., ::-1])
        data = make_image(4)
        assert np.array_equal(rgba.get_conversion_fn_to(rgb)(data), data[..., :3])
        assert np.array_equal(bgra.get_conversion_fn_to(rgb)(data), data[..., :3][..., ::-1])
        data = make_image(1)
        assert np.array_equal(y.get_conversion_fn_to(rgb)(data), np.ones((12, 12, 3), dtype=np.float64))

        # BGR:
        # +-> Row
        data = make_image(3)
        assert np.array_equal(bgr.get_conversion_fn_to(bgr)(data), data)
        assert np.array_equal(bgr.get_conversion_fn_to(rgba)(data), np.concatenate((data[..., ::-1],
                                                                                    make_channel(1)), axis=-1))
        assert np.array_equal(bgr.get_conversion_fn_to(bgra)(data), np.concatenate((data, make_channel(1)), axis=-1))
        assert np.array_equal(bgr.get_conversion_fn_to(y)(data), make_channel(2.1849999999999996))
        # +-> Column
        data = make_image(4)
        assert np.array_equal(rgba.get_conversion_fn_to(bgr)(data), data[..., :3][..., ::-1])
        assert np.array_equal(bgra.get_conversion_fn_to(bgr)(data), data[..., :3])
        data = make_image(1)
        assert np.array_equal(y.get_conversion_fn_to(bgr)(data), np.ones((12, 12, 3), dtype=np.float64))

        # RGBA:
        # +-> Row
        data = make_image(4)
        assert np.array_equal(rgba.get_conversion_fn_to(rgba)(data), data)
        assert np.array_equal(rgba.get_conversion_fn_to(bgra)(data), data[..., (2, 1, 0, 3)])
        assert np.array_equal(rgba.get_conversion_fn_to(y)(data), make_channel(1.815))
        # +-> Column
        data = make_image(4)
        assert np.array_equal(bgra.get_conversion_fn_to(rgba)(data), data[..., (2, 1, 0, 3)])
        data = make_image(1) * 2
        assert np.array_equal(y.get_conversion_fn_to(rgba)(data),
                              np.concatenate((make_channel(2), make_channel(2),
                                              make_channel(2), make_channel(1)), axis=-1))

        # BGRA:
        # +-> Row
        data = make_image(4)
        assert np.array_equal(bgra.get_conversion_fn_to(bgra)(data), data)
        assert np.array_equal(bgra.get_conversion_fn_to(y)(data), make_channel(2.1849999999999996))
        # +-> Column
        data = make_image(1) * 2
        assert np.array_equal(y.get_conversion_fn_to(bgra)(data),
                              np.concatenate((make_channel(2), make_channel(2),
                                              make_channel(2), make_channel(1)), axis=-1))

        # GREY:
        # +-> Row
        data = make_image(1)
        assert np.array_equal(y.get_conversion_fn_to(y)(data), data)

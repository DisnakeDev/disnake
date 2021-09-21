"""
The MIT License (MIT)

Copyright (c) 2015-2021 Rapptz, 2021-present EQUENOS

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
"""

from disnake.opus import APPLICATION_AUDIO, APPLICATION_LOWDELAY, APPLICATION_VOIP, Any, BAD_ARG, BandCtl, CTL_LAST_PACKET_DURATION, CTL_SET_BANDWIDTH, CTL_SET_BITRATE, CTL_SET_FEC, CTL_SET_GAIN, CTL_SET_PLP, CTL_SET_SIGNAL, Callable, Decoder, DecoderStruct, DecoderStructPtr, DiscordException, Encoder, EncoderStruct, EncoderStructPtr, InvalidArgument, List, Literal, OK, Optional, OpusError, OpusNotLoaded, SignalCtl, TYPE_CHECKING, Tuple, TypeVar, TypedDict, _OpusStruct, _err_lt, _err_ne, _lib, _load_default, _log, annotations, array, band_ctl, c_float_ptr, c_int16_ptr, c_int_ptr, ctypes, exported_functions, is_loaded, libopus_loader, load_opus, logging, math, os, overload, signal_ctl, struct, sys
__all__ = ('Encoder', 'OpusError', 'OpusNotLoaded')
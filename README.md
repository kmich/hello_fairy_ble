# Hello Fairy Bluetooth Lights

> Generated with [aurora@aurora-smart-home (ha-integration-dev skill)](https://github.com/tonylofgren/aurora-smart-home)

Control Hello Fairy Bluetooth lights locally from Home Assistant. This combined **1.1.0rc5** candidate preserves existing power, color, brightness and preset controls and adds **Curtain Studio** for supported 400-LED, 20×20 curtains.

One package contains the integration, browser interface, protocol helpers, tests and validation workflows. No separate dashboard card, add-on, web server or cloud account is required.

## What this does

- Import images, paint pixels, choose reusable patterns, and save or reopen designs.
- Save named designs in Home Assistant and play them as an ordered, timed playlist.
- Add pixel text, custom hue palettes, rectangular artwork areas, symmetry, rotation and tiling.
- Recall favorites from generated HA buttons, use named/shuffled playlists, and display occasional clock/message pictures.
- Save named layouts, back up/import the full library, simulate estimated movement locally, and pause/resume playlists with visible transfer progress.
- Arrange curtains left to right on one canvas; two curtains make a 40×20 design.
- Upload two-picture native animations with blink or breathe transitions.
- Set native movement, speed and DIY brightness without another image upload.
- Request timestamped device power, mode, scene and brightness, separately from upload history.
- Inspect native capabilities, use built-in microphone music and supported preset speed, and explicitly manage the device clock, countdown and individual schedules.
- Retry connection setup with bounded backoff; stop failed transfers without automatically replaying image commands.

DIY is experimental. It requires a fresh information response reporting **400 LEDs, 20 columns, 20 rows and DIY type 3**, plus verified transport capacity. Ordinary controls remain available for other models. Pixel readback has not been established: thumbnails show upload history, not a live view.

## Requirements

Home Assistant **2026.9.3 or newer** and a connectable Bluetooth source are required. Automated tests cover 2026.9.3 and 2026.10.1; future versions are not guaranteed.

DIY requires verified ATT MTU **245 or greater** and at least **242 bytes** per write without response. Cached MTU 23 is not accepted as sufficient. The tested ESP32-WROOM-32 proxy with ESPHome 2026.9.1 reported MTU 512 and capacity 509 after fresh preflight. A compatible local Bluetooth adapter is another transport option but has not been physically tested with this candidate.

## Installation

For an existing installation, keep your configured devices:

1. Back up `/config/custom_components/hello_fairy_ble` outside `custom_components`.
2. Copy the complete `custom_components/hello_fairy_ble` folder from this package to that location, including `frontend`, `translations` and every Python file. Copying only `api.py` is insufficient.
3. Restart Home Assistant and refresh the browser.
4. Open **Curtain Studio** in the sidebar as an administrator. Its header or editor footer must show **1.1.0rc5**.

For a new installation, enable Bluetooth and add **Hello Fairy Bluetooth Lights** under **Settings → Devices & services**. The upstream HACS custom repository is `nzrutman/hello_fairy_ble`, category **Integration**. This candidate has not yet been published; HACS cannot download it until a release becomes available.

## Configuration and use

Studio finds loaded curtains automatically. Open **Your Hello Fairy curtains**, choose devices and arrange their order left to right. Changing the layout starts a blank canvas; save your design first.

Choose **Picture** or **Animation**, pick a pattern or image, then press **Send design**. For animation, edit both pictures; switching pictures saves edits automatically. Movement, speed and DIY brightness are sent with the design. **Apply movement** changes playback without uploading the image again.

Speed sends the app's native 0–100 setting, not frames per second. Curtains receive designs sequentially and run independently; synchronized phase or seamless motion across curtains is not guaranteed. Arbitrary video, GIF playback and animations with more than two pictures are not implemented.

## Saved-design library and playlists

Below the editor, open **Design library & playlist**:

1. Create a picture or two-picture animation above. Enter a name and press **Save current design**. This saves it in Home Assistant without sending it to the lights. Saving an existing name offers to replace that design.
2. Use **Open** beside a thumbnail to restore a design to the editor. The number of selected curtains must match its width. Opening does not send it.
3. Press **Add to playlist** for each design you want. Set each step's seconds, use the arrow buttons to reorder, and optionally select **Repeat playlist**.
4. Press **Save playlist**, then **Start on selected curtains**. The selected curtain order is captured when playback starts; changing Studio's layout does not retarget a running playlist.
5. Press **Stop playlist** to finish the current curtain upload and stop further sends. The last design and any native movement remain. A stop during a multi-curtain upload can leave curtains showing different steps; check them before sending again.

There is one shared library with up to 50 designs and **20 named playlists**, with up to 50 steps per playlist. Each step holds for **10–86400 seconds after all uploads complete**, so upload time is additional. This is a slideshow of complete designs, not continuous frame streaming. Different-width designs can coexist in the library, but every step in a running playlist must match the selected curtain count.

Playback runs in Home Assistant and continues after the browser closes. Designs and playlist order survive restarts; playback always starts stopped after a restart. Save edits explicitly. Administrators share the same library. Local design-file download/open remains available separately under the editor's extra tools.

A failed upload or playback-control write stops the playlist without automatic replay or sends to later curtains. Manual Studio sends, Home Assistant light/preset controls, integration unload and HA shutdown stop the playlist before taking over. Phone-app or physical controls cannot be detected reliably and do not automatically stop it.

Automations can start a selected or named playlist, recall a favorite/design, navigate a playlist, or display clock/message pictures. See the complete [Studio guide](STUDIO_GUIDE.md) for the controls, action names, limits and installation corrections. Keep the library in normal Home Assistant backups; do not edit its internal storage file manually.

**Read device status** requests a fresh report. Device reports, last uploads and last playback commands have separate labels and timestamps. History exists only for the current Home Assistant run and may become stale after remote changes or power cycling.

Automation actions are available under `hello_fairy_ble` in **Developer Tools → Actions**, with field descriptions. Standard entities retain their existing identifiers.

## Native curtain controls

Open **Native curtain controls · experimental** above the editor, select one curtain and press **Inspect capabilities**. Inspection reads information and support replies; it changes no design, mode, clock or schedule.

New native controls are restricted to the recorded **model 25025 / firmware 4.6.0 / 400 LEDs / 20×20 / DIY type 3** profile. Music also requires advertised microphone support; preset speed requires a current-connection response and an active known preset; schedules require both complete valid timer banks. These small commands fit ATT MTU 23. Full image uploads keep the separate larger-MTU safeguard.

Music uses the controller microphone, with Energy, Rhythm, Roll and Spectrum patterns, sensitivity, brightness and color options. Clock synchronization, power countdowns and schedule-slot edits are explicit actions. Native schedules use the current fixed timezone offset: review/reapply them after DST or timezone changes. All mutations stop Studio background playback, transmit once and check available readback. Failed readback does not replay the command. No new action runs automatically on restart.

Actual rendered pixels, native text upload, extra storage, true firmware pause and native scene loops remain unverified or unavailable for this model. Existing Studio text, saved designs and software playlists remain available. See [native protocol evidence](NATIVE_EVIDENCE.md) and the [Studio guide](STUDIO_GUIDE.md).

## One controlled rc5 test

Close the phone app. In **Native curtain controls**, choose one curtain and press **Inspect capabilities**. If music is enabled, leave **Energy**, sensitivity 50 and brightness 100 selected, then press **Start music response** once. Play sound near the controller and confirm its visible response. Return to a known preset through HA afterward. If support is unavailable or an error appears, keep the result and check the lights before sending again.

The tester confirmed rc3 and subsequently reported release validation of rc5 on the curtain/proxy setup. A separate feature-by-feature checklist, long-term reliability and future scheduled execution were not recorded. A successful device reply does not prove the visible display. See [VALIDATION.md](VALIDATION.md).

## Troubleshooting

If Studio is missing, confirm the integration loaded, restart after copying all files, and sign in as an administrator. Refresh the browser if its version is stale.

DIY preflight errors identify missing device information, source, MTU or write capacity. No oversized probe or 80-small-packet fallback is attempted. Enable debug logging for `custom_components.hello_fairy_ble` for preflight and transfer timing. Redact device addresses before posting logs publicly.

Connection setup retries at most three times. Notification-subscription error 133 can be retried before image commands begin. After a transfer error, later curtains are not sent and the image is not replayed automatically. Check the lights, then deliberately send again. Close the phone app if it holds the connection.

If a proxy cannot establish verified capacity, diagnose uncached MTU negotiation or use a supported local Bluetooth adapter near the curtain. Do not force larger packets past failed preflight.

## Recovery

Restore the backed-up integration folder and restart Home Assistant. Do not delete existing configured devices. Saved design files can be retained. After an incomplete transfer, use the original app or a deliberate full upload to restore a known design.

## Development

See [NATIVE_EVIDENCE.md](NATIVE_EVIDENCE.md), [PROTOCOL.md](PROTOCOL.md), [VALIDATION.md](VALIDATION.md) and the proposed single [PR description](PR_DESCRIPTION.md).

Baseline: upstream `cc166bc3d847cd8ec6f5f217717403bbf2b60c78`. No APK, decompiled vendor source, raw captures, credentials or vendor image library are included. Existing upstream files and attribution are retained; this package does not establish a new license for upstream code.

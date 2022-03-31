# -*- mode: python ; coding: utf-8 -*-
block_cipher = None


a = Analysis(['udts.py'],
             pathex=[],
             binaries=[],
             datas=[('static','./static'), ('templates','./templates')],
             hiddenimports=[],
             hookspath=[],
             hooksconfig={},
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          a.binaries,
          a.zipfiles,
          a.datas,  
          [],
          name='udts',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          disable_windowed_traceback=False,
          target_arch=None,
          codesign_identity=None,
          entitlements_file=None , icon='static/chhtv.ico')
app = BUNDLE(exe,
             name='udts.app',
             icon='static/chhtv.ico',
             bundle_identifier='com.chhopskytv.updatethestream',
             info_plist={
                'CFBundleName': 'Update The Stream',
                'CFBundleDisplayName': 'Update The Stream',
                'CFBundleVersion': '0.4',
                'CFBundleShortVersionString': '0.4',
                'NSRequiresAquaSystemAppearance': 'No',
                'NSHighResolutionCapable': 'True',
                },
             )

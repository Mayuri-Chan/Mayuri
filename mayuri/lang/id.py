lang_name = "🇮🇩 Indonesia"
text = {
	'select_lang': "Silahkan pilih bahasa yang ingin anda gunakan:",
	'language_changed': "Bahasa berhasil diubah menjadi {}".format(lang_name),
	'pm_me': "Hubungi saya di PM.",
	'not_user': "Itu bukan user!",
	'added_to_sudo': "User {} telah ditambahkan ke SUDO",
	'removed_to_sudo': "User {} telah di hapus dari SUDO",
	'sudo_ls': "Daftar sudo saya:",
	'helps': "Bantuan",
	'this_plugin_help': "Ini adalah bantuan untuk plugin **{}**:\n",
	'back': "Kembali",
	'refreshing_admin': "Merefresh cache admin...",
	'search_zombies': "Mencari akun terhapus...",
	'no_zombies': "Grup bersih. tidak ada akun terhapus :)",
	'found_zombies': "Ditemukan {} akun terhapus.\nMembersihan...",
	'zombies_cleaned': "Berhasil membersihkan {} akun terhapus",
	'admin': "Admin Tools",
	'admin_help': """
Module ini digunakan untuk mengatur grup.
[Admin Tools]
> `/admincache`
Memperbaharui daftar admin.
> `/approve`
Menambahkan user ke whitelist.
> `/unapprove`
Menghapus user dari whitelist.
> `/zombies`
Mencari dan membersihkan akun terhapus.
	""",
	'admin_refreshed': "Cache admin berhasil direfresh.",
	'admin_approved_list': "Daftar user yang diwhitelist di grup ini:",
	'admin_no_approved': "Belum ada user yang diwhitelist di grup ini!",
	'admin_user_added_to_approve': "User {} telah ditambahkan ke daftar whitelist",
	'admin_user_removed_to_approve': "User {} telah dihapus dari daftar whitelist",
	'HELP_STRINGS': """
Kamu dapat menggunakan {} untuk mengeksekusi perintah bot ini.
Perintah **Utama** yang tersedia:
 - /start: mendapatkan pesan start
 - /help: mendapatkan semua bantuan
	""",
	'stickers': "Sticker",
	'stickers_help': """
[Stickers]
> `/stickerid`
Mendapatkan id dari sticker yang dibalas

> `/getsticker`
Untuk mendapatkan sticker yang dibalas dalam bentuk gambar/video (png/webm)

> `/kang`
Untuk mencuri sticker.
	""",
	'your_stickerid': "Id sticker yang anda balas :\n{}",
	'must_reply_to_sticker': "Anda harus membalas pesan sticker untuk menggunakan perintah ini!",
	'animated_not_supported': "Stiker animasi tidak didukung!",
	'use_whisely': "Gunakan fitur ini dengan bijak!\nSilahkan cek gambar dibawah ini :)",
	'processing': "Memproses...",
	'cannot_kang': "Itu tidak dapat di Kang!",
	'creating_pack': "Membuat Stickerpack...",
	'cannot_create_pack': "Terjadi kesalahan saat membuat Stickerpack!",
	'show_pack': "Lihat Stickerpack",
	'sticker_kanged': "Sticker berhasil dikang.",
	'blacklist': "Daftar hitam",
	'blacklist_help': """Module ini digunakan untuk melarang penggunaan suatu kata dalam pesan.
[Word Blacklist]
> `/addbl <kata> [<mode>] [<waktu>] [<alasan>]`
Menambahkan kata kedalam daftar hitam
contoh :
> `/addbl anu`
> `/addbl anu kick`
> `/addbl anu mute 12h`

> `/rmbl <kata>`
Menghapus kata dari daftar hitam
contoh :
> `/rmbl anu`

> `/blacklist`
Menampilkan daftar kata yang ada di daftar hitam

[Mode]
Opsional, mode defaultnya adalah delete
- delete	- ban
- kick		- mute

[Waktu]
Khusus mode mute dan ban (Opsional)
daftar unit waktu :
- s = detik
- m = menit
- h = jam
- d = hari
	""",
	'blacklist_added': "<code>{}</code> Telah ditambahkan ke GBlacklist dengan mode {}",
	'blacklist_duration': " dan durasi selama {}",
	'blacklist_reason': ".\nAlasan: {}",
	'blacklist_deleted': "<code>{}</code> Berhasil dihapus dari Blacklist!",
	'cannot_remove_blacklist': "<code>{}</code> Gagal dihapus dari Blacklist!",
	'what_blacklist_to_remove': "Apa yang mau dihapus dari Blacklist?",
	'blacklist_list': "Daftar kata yang diblacklist di Grup ini:\n",
	'no_blacklist': "Tidak ada kata yang diblacklist di Grup ini!",
	'muted': "Dibisukan",
	'kicked': "Ditendang",
	'banned': "Dibanned",
	'blacklist_for': " selama {}",
	'user_and_reason': "\nUser : {}\nAlasan :",
	'blacklist_said': " Mengatakan <code>{}</code>",
	'filters': "Filters",
	'filters_help': """
Module ini digunakan untuk membuat reply otomatis untuk suatu kata.
[Filters]
> `/filter <kata> <balasan`
Menambahkan filter baru

> `/stop <kata>`
Menghapus filter

> `/filters`
Mendapatkan daftar filter aktif
	""",
	'give_filter_name': "Anda harus memberikan nama untuk filter ini!",
	'give_filter_text': "Anda harus menambahkan teks untuk filter ini, tidak bisa menggunakan button saja!",
	'filter_added': "Handler <code>{}</code> Telah ditambahkan di {}",
	'filter_removed': "Saya akan berhenti membalas <code>{}</code> di {}!",
	'filter_not_found': "<code>{}</code> Bukan filter aktif!",
	'what_filter_to_remove': "Apa yang mau dihapus dari filter?",
	'filter_list': "Daftar filters di Grup ini:\n",
	'no_filter_found': "Tidak ada filters di {}!",
	'blpack': "Daftar Hitam Stickerpack",
	'blpack_help': """Module ini digunakan untuk melarang penggunaan semua sticker dalam suatu Stickerpack.
[Stickerpack Blacklist]
> `/addblpack [<mode>] [<waktu>] [<alasan>]`
Menambahkan stickerpack kedalam daftar hitam
contoh :
> `/addblpack`
> `/addblpack kick`
> `/addblpack mute 12h`

> `/rmblpack`
Menghapus stickerpack dari daftar hitam
contoh :
> `/rmblpack`

> `/blpack`
Menampilkan daftar stickerpack yang ada di daftar hitam

[Mode]
Opsional, mode defaultnya adalah delete
- delete	- ban
- kick		- mute

[Waktu]
Khusus mode mute dan ban (Opsional)
daftar unit waktu :
- s = detik
- m = menit
- h = jam
- d = hari
	""",
	'blpack_added': "Sticker Pack <code>{}</code> Telah ditambahkan ke Blacklist dengan {}",
	'blpack_deleted': "Sticker Pack <code>{}</code> Berhasil dihapus dari Blacklist!",
	'cannot_remove_blpack': "Sticker Pack <code>{}</code> Gagal dihapus dari Blacklist!",
	'blpack_list': "Daftar Sticker Pack yang diblacklist di Grup ini:\n",
	'no_blpack': "Tidak ada Sticker Pack yang diblacklist di Grup ini!",
	'blpack_send': "Mengirimkan sticker yang ada di pack <code>{}</code>",
	'blsticker': "Daftar Hitam Sticker",
	'blsticker_help': """Module ini digunakan untuk melarang penggunaan suatu sticker.
[Sticker Blacklist]
> `/addblsticker [<mode>] [<waktu>] [<alasan>]`
Menambahkan stickerpack kedalam daftar hitam
contoh :
> `/addblsticker`
> `/addblsticker kick`
> `/addblsticker mute 12h`

> `/rmblsticker`
Menghapus sticker dari daftar hitam
contoh :
> `/rmblsticker`

> `/blsticker`
Menampilkan daftar sticker yang ada di daftar hitam

[Mode]
Opsional, mode defaultnya adalah delete
- delete	- ban
- kick		- mute

[Waktu]
Khusus mode mute dan ban (Opsional)
daftar unit waktu :
- s = detik
- m = menit
- h = jam
- d = hari
	""",
	'blsticker_added': "Sticker <code>{}</code> Telah ditambahkan ke Blacklist dengan {}",
	'blsticker_deleted': "Sticker <code>{}</code> Berhasil dihapus dari Blacklist!",
	'cannot_remove_blsticker': "Sticker <code>{}</code> Gagal dihapus dari Blacklist!",
	'blsticker_list': "Daftar Sticker yang diblacklist di Grup ini:\n",
	'no_blsticker': "Tidak ada Sticker yang diblacklist di Grup ini!",
	'blsticker_send': "Mengirimkan sticker <code>{}</code>",
	'disable': "Disable Commands",
	'disable_help': """Modul ini digunakan untuk menon-aftikan penggunaan perintah didalam grup
[Disable Commands]
> `/disable <perintah>`
Untuk menonaktifkan perintah
contoh :
> `/disable adminlist`

> `/enable <perintah>`
Untuk mengaktifkan kembali perintah yang telah di non-aktifkan
contoh :
> `/enable adminlist`

> `/disabled`
Untuk menampilkan daftar perintah yang telah di non-aktifkan

> `/disableable`
Untuk menampilkan daftar perintah yang dapat di non-aktifkan
	""",
	'cmd_not_found': "Perintah {} tidak tersedia!",
	'cmd_disabled': "Perintah {} berhasil dinon-aktifkan!",
	'what_cmd_to_disable': "Perintah apa yang mau dinon-aktifkan?",
	'cmd_enabled': "Perintah {} berhasil diaktifkan!",
	'what_cmd_to_enable': "Perintah apa yang mau diaktifkan?",
	'disabled_list': "Daftar Perintah yang dinon-aktifkan di grup ini:\n",
	'no_cmd_disabled': "Tidak ada Perintah yang dinon-aktifkan di grup ini!",
	'can_disabled': "Daftar Perintah yang dapat dinon-aktifkan:\n",
	'need_user_id': "Berikan username atau id user!",
	'why_gban_owner': "Kenapa saya harus gban master saya?",
	'why_gban_sudo': "Kenapa saya harus gban sudo saya?",
	'why_gmute_owner': "Kenapa saya harus gmute master saya?",
	'why_gmute_sudo': "Kenapa saya harus gmute sudo saya?",
	'why_gdmute_owner': "Kenapa saya harus gdmute master saya?",
	'why_gdmute_sudo': "Kenapa saya harus gdmute sudo saya?",
	'why_ungdmute_sudo': "Hanya Owner yang dapat ungdmute sudo!",
	'gbanned': "User {} telah di ban secara global",
	'gmuted': 'User {} telah di mute secara global',
	'gdmuted': 'User {} telah di dmute secara global',
	'ungbanned': "User {} telah di unban secara global",
	'ungmuted': 'User {} telah di unmute secara global',
	'ungdmuted': 'User {} telah di undmute secara global',
	'user_in_gban': 'User {} ada di daftar global ban dan telah dibanned dari grup!',
	'user_in_gmute': 'User {} ada di daftar global mute dan telah dibisukan!',
	'restrict_time_left': "\nSisa waktu: {}",
	'new_gban': "#GBAN\n**Global Ban Baru**",
	'new_gmute': "#GMUTE\n**Global Mute Baru**",
	'new_gdmute': "#GDMUTE\n**Global Delete Mute Baru**",
	'new_ungban': "#UNGBAN\n**Lepas Global Ban Baru**",
	'new_ungmute': "#UNGMUTE\n**Lepas Global Mute Baru**",
	'new_ungdmute': "#UNGDMUTE\n**Lepas Global Delete Mute Baru**",
	'geting_info': "Mendapatkan info...",
	'infouser_info': "**Informasi User**",
	'infouser_id': "\nID: `{}`",
	'infouser_firstname': "\nNama depan: {}",
	'infouser_lastname': "\nNama belakang: {}",
	'infouser_name': "\nNama pengguna: @{}",
	'infouser_link': "\nLink: [link](tg://user?id={})",
	'infouser_in_gban': "\n\nUser ada didaftar gban.",
	'infouser_in_gmute': "\n\nUser ada didaftar gmute.",
	'infouser_in_gdmute': "\n\nUser ada didaftar gdmute.",
	'infouser_date': "\nTanggal: {}",
	'infouser_sudo': "\nSudo: {}",
	'infouser_duration': "\nDurasi: {}",
	'infouser_is_channel': "Tolong reply ke pengguna bukan channel!",
	'cas_log': "#CAS_GBAN\nCAS Global Ban Baru.\nChat: @{}\nPengguna: {}\nID Pengguna: `{}`\nAlasan: {}",
	'cas_msg': "User {} telah di ban secara global\nAlasan: {}\n\nPowered by: Combot Anti Spam API",
	'welcome_set': "Pesan Sambutan berhasil diatur",
	'not_forum': "Grup ini bukan forum. silahkan hidupkan option topic terlebih dahulu!",
	'welcome_not_set': "Pesan sambutan belum diatur di grup ini!",
	'thread_id_set': "Berhasil.\nSemua pesan sambutan akan dikirim ke topic ini.",
	'welcome_enabled': "Pesan sambutan diaktifkan!",
	'welcome_disabled': "Pesan sambutan dinon-aktifkan!",
	'welcome_settings': "**Pengaturan Pesan Sambutan:**\nAktif: {}\nPembersih Pesan Layanan: {}\nForum Thread ID: `{}`",
	'default-welcome': "Selamat datang {first} di Grup {chatname}!",
}

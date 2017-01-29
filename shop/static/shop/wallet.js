$('#newaddressmodal').on('hidden.bs.modal', function (e) {
	app.data.walletname = ''
	app.data.errors = [];
});

var app = new Vue({
	el: '#vue-app',
	data: {
		wallets: wallets,
		balance: totalbalance,
		pending: totalpending,
		errors: [],
		disableaddress: false,
		disablesend: true,
		walletname: '',
		to_address: '',
		fee: 1,
		ammount: 0,
		selectedwallet: 0,
		validaddress: false,
		validammount: false,
		validlength: false,
		disablesend: false,
	},
	methods: {
		newwallet: function() {
			this.errors = [];
			if (this.walletname.length <= 30) {
				var r = new XMLHttpRequest();
				r.open('POST', newwallet_url, true);
				r.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
				r.send('wallet_name='+this.walletname);

				this.disableaddress = true;

				var t = this;
				r.onload = function(e) {
					t.disableaddress = false;
					var wallet = JSON.parse(r.responseText);
					if (wallet.redirect) {
						window.location = wallet.redirect;
					}
					if (wallet.status == 'success') {
						t.balance = wallet.wallet.totalbal;
						t.pending = wallet.wallet.totalpend;

						var newaddr = {
							label: wallet.wallet.label,
							balance: wallet.wallet.balance,
							pending: wallet.wallet.pending,
							address: wallet.wallet.address,
							id: wallet.wallet.id,
						};
						wallets.push(newaddr);

						t.errors = [];
						t.walletname = '';
						$('#newaddressmodal').modal('hide');
					} else {
						t.errors = wallet.errors;
					}
				}
			} else {
				this.errors.push("Wallet name has to be 30 characters or less.");
			}
		},
		sendto: function() {
			this.errors = [];
			this.checklength();
			this.checkammount();
			if (this.validaddress && this.validammount && this.validlength) {
				r = new XMLHttpRequest();
				r.open('POST', send_url, true);
				r.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
				r.send('wallet='+this.wallets[this.selectedwallet].id+'&ammount='+this.ammount+'&address='+this.to_address)
				this.disablesend = true;

				var t = this;
				r.onload = function(e) {
					t.disablesend = false;
					var re = JSON.parse(r.responseText);
					if (re.redirect) {
						window.location = re.redirect;
					}
					if (re.status == 'success') {
						t.balance = re.balance;
						t.pending = re.pending;
						t.wallets = re.wallets;
						$('#sendtomodal').modal('hide');
					} else {
						t.errors = re.errors;
					}
				}
			}
		},
		checklength: function() {
			this.errors = [];
			if (this.walletname.length > 30) {
				this.errors.push("Wallet name has to be 30 characters or less.");
			}
			this.disableaddress = this.walletname.length > 30;
		},
		checkaddrlength: function() {
			this.validlength = this.to_address.length == 34
			if (this.to_address.length == 34) {
				var r = new XMLHttpRequest();
				r.open('GET', checkaddr_url+'?address='+this.to_address, true);
				r.send();
				var t = this;
				r.onload = function(e) {
					var re = JSON.parse(r.responseText);
					if (re.status == 'success') {
						if (re.valid) {
							if (re.type == 'external') {
								t.fee = 1;
							} else {
								t.fee = 0;
							}
							t.validaddress = true;
						} else {
							t.errors.push('Invalid address');
							t.validaddress = false;
						}
					} else {
						t.errors = re.errors;
					}
				}
			}
		},
		checkammount: function() {
			this.errors = [];
			if (this.ammount + this.fee > this.wallets[this.selectedwallet].balance) {
				this.errors.push("Not enough funds.");
			}
			if (this.ammount <= 0) {
				this.errors.push("You have to send more than 0 OK.");
			}
			this.validammount = this.ammount > 0 && this.ammount + this.fee <= this.wallets[this.selectedwallet].balance;
		}
	}
});
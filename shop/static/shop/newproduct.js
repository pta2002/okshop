var app = new Vue({
	el: '#vue-app',
	data: {
		'product_name': '',
		'stock': 0,
		'physical': true,
		'currency': 'OK',
		'free_shipping': false,
		'unlimited': false,
		'worldwide': true,
		'images': [],
		'price': 0,
		'localprice': 0,
		'globalprice': 0,
	},
	methods: {
		'uploadfiles': function(e) {
			files = e.target.files || e.dataTransfer.files;
			formdata = new FormData();
			for (file of files) {
				if (!file.type.match("image.*")) {
					continue;
				}

				formdata.append('pics', file, file.name);
			}
			xhr = new XMLHttpRequest();
			xhr.open('POST', '/api/uploadpic/', true);

			var t = this;
			xhr.onload = function() {
				re = JSON.parse(xhr.responseText);
				t.images = t.images.concat(re.images);
			}
			xhr.send(formdata);
			document.getElementById("upload-pic").value = "";
		},
		'delpic':function(index){
			pic = this.images.splice(index,1);
			xhr = new XMLHttpRequest();
			xhr.open('GET', '/api/deletepic/' + pic[0].delete + '/')
			xhr.send();
		}
	}
});
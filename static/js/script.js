/*
Zak Yeomanson
Applications of Programming Principles
Full Stack App: JavaScript

Date Issued: 6th February 2020
Submission Due Date: 29th May 2020
 */

//Constant variable. I set this to 6 to display only 6 users per page on my web app
const PER_PAGE = 6;

let total_pages = 0;


const sendHttpRequest = (method, url, data) => {
	/** Wraps an XMLHttpRequest in a Promise. Resolves the response if it can, and sends the JSON data if it exists
	 *
	 * @param {string} method - The http method, e.g GET, POST
	 * @param {string} url - The url to request
	 * @param {object} [data] - OPTIONAL: The JSON data in a dictionary/JSON format. Used with certain methods
	 */

	return new Promise((resolve) => {
		const xhr = new XMLHttpRequest();
		xhr.open(method, url);

		xhr.responseType = "json";

		if (data) {
			xhr.setRequestHeader("content-type", "application/json");
		}


		xhr.onload = () => {
			if (xhr.readyState === 4 && xhr.status >= 200 && xhr.status < 300) { // Between 200 and 300 are OK responses
				resolve(xhr.response);
			}

		};

		xhr.send(JSON.stringify(data));


	});
	
};


const createNewUser = () => {
	/** Sends a POST request along with the username and job given on the website.
	 *  Function called when the "New User" button is pressed.
	 */

	// Grab all the information we need
	let email = document.getElementById("newUserEmail").value;
	let firstName = document.getElementById("newUserFirstName").value;
	let lastName = document.getElementById("newUserLastName").value;
	let avatar = document.getElementById("newAvatar").value;
	
	// Now send all the information and create the user
	sendHttpRequest("POST", "http://127.0.0.1:5000/api/users/create", {
		"email": email,
		"first_name": firstName,
		"last_name": lastName,
		"avatar": avatar
	}).then(() => {
		//Refresh, ignoring cache
		location.reload(true); //Pycharm states this as deprecated but it does what we need
	});
	
	
};


const deleteUser = () => {
	/** Sends a DELETE request with the userID given.
	 *  Function called when the "Delete User" button is pressed
	 */
	
	let userID = document.getElementById("userID").value;
	sendHttpRequest("DELETE", "http://127.0.0.1:5000/api/users/delete/".concat(userID)).then(() => {
		location.reload(true); //Refresh the page
	});
	
};


const updateUser = () => {
	/** Sends a PUT request with the data given to update the changes of a user.
	 *  Function called when the "Save Changes" button is pressed
	 */
	
	let userID = document.getElementById("userID").value;
	let email = document.getElementById("userEmail").value;
	let firstName = document.getElementById("userFirstName").value;
	let lastName = document.getElementById("userLastName").value;

	
	sendHttpRequest("PUT", "http://127.0.0.1:5000/api/users/".concat(userID), {
		"id": userID,
		"email": email,
		"first_name": firstName,
		"last_name": lastName
	}).then(() => {
		location.reload(true); //Refresh the page
	});
	
};

const prevPage = () => {
	/** Modifies the page displayed on the browser and loads the previous page, if it exists
	 */
	let pageNum = document.getElementById("pageNumber");
	let pageToLoad = parseInt(pageNum.innerText)-1

	if(pageToLoad <= 0){
		return;
	}

	loadUsers(pageToLoad);

	
};

const nextPage = () => {
	/** Modifies the page displayed on the browser and loads the next page, if it exists
	 */
	let pageNum = document.getElementById("pageNumber");
	let pageToLoad = parseInt(pageNum.innerText)+1

	loadUsers(pageToLoad);

};



const clearUsers = () => {
	/** Completely clears the table, so no users exist on the web page
	 */
	for(let i=1; i <= PER_PAGE; i++){
		let row = document.getElementById("user"+String(i));
		row.innerHTML = "<td></td><td></td><td></td><td></td><td><img src=\"\" alt=\"\"></td>";
	}
}


function loadUsers(page) {
	/** Calls my API for the page specified, and loads each row in the HTML table of the correct users
	 *
	 * @param {int} page - The page number to load. Only loads valid pages
	 */


	if(total_pages !== 0 && page > total_pages){ //Invalid page !
		return;
	}


	sendHttpRequest("GET", "http://127.0.0.1:5000/api/users/page/".concat(page)).then(responseData => {

		/* Example responseData may look like:
			responseData = {"total_pages":1,
							"data":[{"id":1,"email":"z@gmail.com","first_name":"Z","last_name":"Y","avatar":"h.png"},
									{"id":2, "email":"x@gmail.com","first_name":"H","last_name":"X","avatar":"x.png"}]}
		 */

		total_pages = responseData["total_pages"];

		// Change the page numbers
		let pageNum = document.getElementById("pageNumber");
		pageNum.innerText = page;

		let totalPages = document.getElementById("totalPages");
		totalPages.innerText = responseData["total_pages"];

		// Clear the user table
		clearUsers();

		// Fill up each row in the table
		for (let i = 0; i < responseData["data"].length; i++) {

			let userID = responseData["data"][i]["id"];

			let email = responseData["data"][i]["email"];
			let firstName = responseData["data"][i]["first_name"];
			let lastName = responseData["data"][i]["last_name"];
			let avatar = responseData["data"][i]["avatar"];

			//Edit each HTML row and fill it with our data dynamically
			let row = document.getElementById("user"+ String(i+1));
			row.innerHTML = "<td>" + userID + "</td><td>" + email + "</td><td>" + firstName + "</td><td>" + lastName +
				"</td><td><img onclick=\"showUser(this)\" src=\"" + avatar + "\" alt=\"avatar\" width=\"128\""+
				" height=\"128\"></td>";
		}


	});
}

function showUser(element){
	/** Displays the user's information on the screen, based on the element parameter.
	 *
	 * @param {string} element - The element given through onclick=""
	 */

	//This following line works differently on different web browsers.
	// On Chrome & Firefox, the .innerText variable seperates each text with a tab (\t)
	//But on Microsoft Edge, it uses a newline (\n)
	//Therefore, I first try \t and if it doesn't work, I'll move on to using \n
	//So now this will be compatible for Microsoft Edge users also
	let row = element.parentElement.parentElement.innerText.split("\t");

	if(row.length === 1){ //Their web browser most likely separates innerText with \n
		row = element.parentElement.parentElement.innerText.split("\n");
	}
	let avatar = document.getElementById("userAvatar");
	let userIDInput = document.getElementById("userID");
	let userEmail = document.getElementById("userEmail");
	let userFirstName = document.getElementById("userFirstName");
	let userLastName = document.getElementById("userLastName");

	avatar.src = element.src;

	//Now we have all the inputs, we can change their value
	userIDInput.value = row[0];
	userEmail.value = row[1];
	userFirstName.value = row[2];
	userLastName.value = row[3];

	//Make the userID input field read only, so it cannot be modified!
	userIDInput.readOnly = true;
}

function main(){
	/** main() function, run when the JS is loaded.
	 *  Sets up all the buttons and gives them clicking functionality,
	 *  also loads the first page of users via ajax
	 */
	let getPrevBtn = document.getElementById("btnPrevious");
	let getNextBtn = document.getElementById("btnNext");
	let deleteUserBtn = document.getElementById("btnDeleteUser");
	let saveChangesBtn = document.getElementById("btnSaveUser");
	let newUserBtn = document.getElementById("btnNewUser");


	getPrevBtn.addEventListener("click", prevPage);
	getNextBtn.addEventListener("click", nextPage);

	saveChangesBtn.addEventListener("click", e => {
		e.preventDefault(); //Prevent the default action (to refresh). We refresh the page after we update the users.
		//By default it refreshes before (too early, so we prevent this)
		updateUser(e);
	});
	deleteUserBtn.addEventListener("click",e => {
		e.preventDefault();
		deleteUser(e);

	});
	newUserBtn.addEventListener("click", e => {
		e.preventDefault();
		createNewUser(e);
	});

	loadUsers(1);
}

//Initially run our main() function
main();
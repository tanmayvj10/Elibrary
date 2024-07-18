# Elibrary - Library Management System

Elibrary is a comprehensive web application designed to manage library operations efficiently. Built using HTML, CSS, JavaScript, Flask Framework, SQL Alchemy, SQLite, and Python, it provides interfaces for users, librarians, and administrators, each with distinct functionalities to streamline library management.

## Table of Contents
- [Introduction](#introduction)
- [Features](#features)
  - [Admin Interface](#admin-interface)
  - [Librarian Interface](#librarian-interface)
  - [User Interface](#user-interface)
- [Models](#models)
- [Overall System Design](#overall-system-design)
- [Installation](#installation)
- [Usage](#usage)
- [Utilities and Use Cases](#utilities-and-use-cases)
- [Future Enhancements](#future-enhancements)
- [Constraints/Limitations](#constraints-limitations)
- [Demo Video](#demo-video)

## Introduction

The Library Management System (LMS) is a comprehensive software solution designed to streamline the operations of libraries, facilitating efficient management of books, users, requests, and inventory. This report provides an overview of the system's models and overall design.

## Features

### Admin Interface
- **Manage Librarians**: Admins can create new librarian accounts and manage existing ones.
- **Subscription Management**: Admins can approve or revoke user requests for prime content subscriptions.
- **Statistics and Analytics**: Access to comprehensive statistics about library operations.

### Librarian Interface
- **Section Management**: Create and manage sections, including assigning names and descriptions.
- **Book Management**: Add new books with detailed information (name, author, description) to sections.
- **Issue Management**: Grant and revoke access to books issued to users. Auto-revoke access once the deadline is passed.
- **Review Moderation**: Read and remove false reviews to maintain integrity.
- **Analytics**: View bar graphs for book ratings and average ratings.

### User Interface
- **Dashboard**: Overview of user's activities and access.
- **My Books**: Display books issued to the user.
- **Book Requests**: Request books for a certain number of days.
- **Favorites and Reviews**: Add books to favorites, mark as complete, and provide ratings and reviews.
- **Prime Subscription**: Request for prime subscription.
- **Profile Management**: Update personal details. View pie charts showing book sections most issued.

## Models

<details>
  <summary>User</summary>
  
| Field      | Type          | Description       |
|------------|---------------|-------------------|
| Id         | Primary Key   | Unique identifier |
| Username   | String        | User's username   |
| Passhash   | String        | Password hash     |
| Name       | String        | Full name         |
| Age        | Integer       | Age               |
| User_img   | String (URL)  | User image URL    |

</details>

<details>
  <summary>Librarian</summary>
  
| Field      | Type          | Description       |
|------------|---------------|-------------------|
| Lib_id     | Primary Key   | Unique identifier |
| Passhash   | String        | Password hash     |
| Name       | String        | Full name         |
| Lib_img    | String (URL)  | Librarian image URL|

</details>

<details>
  <summary>Admin</summary>
  
| Field      | Type          | Description       |
|------------|---------------|-------------------|
| Admin_id   | Primary Key   | Unique identifier |
| Passhash   | String        | Password hash     |
| Name       | String        | Full name         |
| Admin_img  | String (URL)  | Admin image URL   |

</details>

<details>
  <summary>Books</summary>
  
| Field      | Type          | Description       |
|------------|---------------|-------------------|
| Id         | Primary Key   | Unique identifier |
| Book_title | String        | Title of the book |
| Author     | String        | Author's name     |
| Description| String        | Book description  |
| Link       | String (URL)  | Book link (PDF)   |
| Section_id | Foreign Key   | Section identifier|
| Book_cover | String (URL)  | Book cover image  |
| Added_by   | Foreign Key   | Librarian who added the book |
| Date_added | Date          | Date when added   |

</details>

<details>
  <summary>Sections</summary>
  
| Field      | Type          | Description       |
|------------|---------------|-------------------|
| Section_id | Primary Key   | Unique identifier |
| Section    | String        | Section name      |
| Description| String        | Section description |
| Added_by   | Foreign Key   | Librarian who added the section |
| Prime      | Boolean       | Prime section flag|
| Date_added | Date          | Date when added   |

</details>

<details>
  <summary>Books Issued</summary>
  
| Field      | Type          | Description       |
|------------|---------------|-------------------|
| Issue_id   | Primary Key   | Unique identifier |
| Book_id    | Foreign Key   | Issued book id    |
| User_id    | Foreign Key   | User id           |
| Issued_by  | Foreign Key   | Librarian who issued the book |
| Issue_date | Date          | Date of issue     |
| Access_date| Date          | Access expiration date |

</details>

<details>
  <summary>Book Reviews</summary>
  
| Field      | Type          | Description       |
|------------|---------------|-------------------|
| Review_id  | Primary Key   | Unique identifier |
| Book_id    | Foreign Key   | Reviewed book id  |
| User_id    | Foreign Key   | User id           |
| Rating     | Integer       | Book rating       |
| Reviews    | Text          | Review text       |

</details>

<details>
  <summary>Book Completed</summary>
  
| Field      | Type          | Description       |
|------------|---------------|-------------------|
| Record     | Primary Key   | Unique identifier |
| Book_id    | Foreign Key   | Completed book id |
| User_id    | Foreign Key   | User id           |

</details>

<details>
  <summary>Favourites</summary>
  
| Field      | Type          | Description       |
|------------|---------------|-------------------|
| Fav_id     | Primary Key   | Unique identifier |
| Book_id    | Foreign Key   | Favourite book id |
| User_id    | Foreign Key   | User id           |

</details>

<details>
  <summary>User Req</summary>
  
| Field      | Type          | Description       |
|------------|---------------|-------------------|
| Req_id     | Primary Key   | Unique identifier |
| Book_id    | Foreign Key   | Requested book id |
| User_id    | Foreign Key   | User id           |
| Days       | Integer       | Requested days    |

</details>

<details>
  <summary>Prime</summary>
  
| Field      | Type          | Description       |
|------------|---------------|-------------------|
| User_id    | Primary Key   | Unique identifier |

</details>

<details>
  <summary>Prime Req</summary>
  
| Field      | Type          | Description       |
|------------|---------------|-------------------|
| User_id    | Primary Key   | Unique identifier |

</details>

## Overall System Design

1. **User Authentication and Authorization**
   - Users can register, login, and update their profiles.
   - Librarians have additional privileges to manage books, sections, and user requests.
   - Admins can create new librarians.

2. **Book Management**
   - Librarians can add, update, and delete books and sections.
   - Users can browse books by sections, view book details, and borrow books.

3. **Request Management**
   - Users can request to borrow books, which are approved or denied by librarians.
   - Upon approval, the book is issued to the user with a return date.
   - Users can return books.
   - Users can submit feedback/reviews for the books.
   - Users can request a prime subscription, which can be granted by the admin, giving access to special sections.

4. **Reporting and Analytics**
   - Admins have access to reports showing book statistics, user activities, and section categories.
   - Analytics help optimize inventory management and user experience.

5. **Other Features for User Experience**
   - Latest books appear on the top for user browsing.
   - Users can mark a book as read/completed.
   - Users can mark books as favorites.

## Installation

To install and run Elibrary on your local machine:

1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/elibrary.git
   cd elibrary
   ```

2. Set up a virtual environment:
   ```sh
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install the required packages:
   ```sh
   pip install -r requirements.txt
   ```

4. Set up the database:
   ```sh
   flask db init
   flask db migrate -m "Initial migration."
   flask db upgrade
   ```

5. Run the application:


   ```sh
   flask run
   ```

## Usage

After starting the application, navigate to `http://localhost:5000` in your web browser to access the Elibrary system.

## Utilities and Use Cases

Elibrary can be used by educational institutions, public libraries, and private collections to manage their book inventory, subscriptions, and user interactions effectively. The web application provides a user-friendly interface for different roles, ensuring efficient library operations.

## Future Enhancements

- **Enhanced Search Functionality**: Implement advanced search filters for books and sections.
- **Notification System**: Add email/SMS notifications for book due dates, new arrivals, and subscription status.
- **Mobile Responsiveness**: Improve UI for better usability on mobile devices.
- **Machine Learning**: Integrate recommendation systems for book suggestions based on user history and preferences.

## Constraints/Limitations

- If a section is deleted, books under the section are also deleted.
- A book can be deleted even if it is issued to a user.
- The image available for each book is a default stock image until changed.
- While adding a book to the library, it is mandatory for the librarian to upload its PDF.

## Demo Video

Watch the demo video [here](https://www.youtube.com/watch?v=sY6bAyTGYHs).


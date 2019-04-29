import {Component, HostListener, OnInit} from '@angular/core';
import { NgModule } from '@angular/core';
import {BrowserAnimationsModule} from '@angular/platform-browser/animations';
import * as firebase from 'firebase';
import {MatDialog, MatDialogRef, MAT_DIALOG_DATA} from '@angular/material';
import {SetNameComponent} from './set-name/set-name.component';
import {PersonInfoComponent} from './person-info/person-info.component';


@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
})


export class AppComponent implements OnInit {

  constructor(public dialog: MatDialog) {}
  public static people: any;
  title = 'iot-fe';
  public selfColumns = 1;
  public people: any;
  public allPeople: any;
  private orderedPeople = [];

  ngOnInit() {
    this.selfColumns = Math.floor(document.body.clientWidth / 325);
    this.getData();
  }

  getData() {
    const config = {
    };
    firebase.initializeApp(config);
    const storage = firebase.storage();
    firebase.database().ref('/people').limitToLast(10000).once('value').then(snapshot => {
      this.allPeople = snapshot.val();
      Object.keys(this.allPeople).forEach( person => {
        const name = Object.keys(this.allPeople[person].visits)[0] + '.jpg';
        storage.ref().child(name).getDownloadURL().then(url => {
          this.allPeople[person]['url'] = url;
        });
        });
      });
    firebase.database().ref('/people').orderByChild('most_recent').limitToLast(20).once('value').then(snapshot => {
      this.people = snapshot.val();
      for (let [key, value] of Object.entries(this.people)) {
        this.people[key].visar = [];
        this.people[key].selected = 0;
        let temp = value;
        temp['id'] = key;
        this.orderedPeople.push(temp);
        Object.keys(this.people[key].visits).forEach( key2 => {
          const name = key2 + '.jpg';
          storage.ref().child(name).getDownloadURL().then(url => {
            const sub = 'url';
            this.people[key].visits[key2][sub] = url;
            this.people[key].visar.push(this.people[key].visits[key2]);
            this.people[key].max_slide = this.people[key].visar.length - 1;
            //console.log(this.people[key].visar.length);
            this.people[key]['visar'].sort(this.compare_visit);
          });
        });
      }
      this.orderedPeople.sort(this.compare_most_recent);
      setTimeout(() => {
        console.log(this.orderedPeople);
      }, 1000);
    });
  }

  @HostListener('window:resize', ['$event'])
  onResize(event) {
    const width = event.target.innerWidth;
    this.selfColumns = Math.floor(width / 325);
  }

  objectKeys(input) {
    return Object.keys(input);
  }

  objectLen(input) {
    return Object.keys(input).length;
  }

  updateImage(person, input) {
    this.people[person].selected = input;
  }

  compare(a, b) {
    const sa = Object.keys(a.visits).length;
    const sb = Object.keys(b.visits).length;
    let comparison = 0;
    if (sa < sb) {
      comparison = 1;
    } else if (sb < sa) {
      comparison = -1;
    }
    return comparison;
  }

  compare_most_recent(a, b) {
    const sa = a.most_recent;
    const sb = b.most_recent;
    let comparison = 0;
    if (sa < sb) {
      comparison = 1;
    } else if (sb < sa) {
      comparison = -1;
    }
    return comparison;
  }

  compare_visit(a, b) {
    const sa = a['timestamp'];
    const sb = b['timestamp'];
    let comparison = 0;
    if (sa < sb) {
      comparison = 1;
    } else if (sb < sa) {
      comparison = -1;
    }
    return comparison;
  }



  openNameDialog(person, id): void {
    const dialogRef = this.dialog.open(SetNameComponent, {
      width: '600px',
      data: {name: person.name}
    });

    dialogRef.afterClosed().subscribe(result => {
      console.log('The dialog was closed');
      person.name = result;
      if (!person.name) {
        person.name = 'unknown';
      }
      firebase.database().ref('/people').child(id).child('name').set(person.name);
    });
    }

  openChartDialog(person, id): void {
    let allData = {};
    allData['person'] = person;
    allData['id'] = id;
    allData['people'] = this.allPeople;
    const dialogRef = this.dialog.open(PersonInfoComponent, {
      width: (document.body.clientWidth - 50) as unknown as string,
      data: allData
    });

    dialogRef.afterClosed().subscribe(result => {
    });
  }
}



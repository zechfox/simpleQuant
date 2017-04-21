import { LogService, LogMessage } from './log.service';
import { Component, ElementRef, Input, OnInit } from '@angular/core';
import { Subject } from 'rxjs/Rx';

@Component({
  selector: 'log',
  template: `
            <div class="messages">
            <p *ngFor="let msg of logMessages">{{ msg.message }}</p>
            </div>
            <button (click)="connect()">Connect</button>
	    <button (click)="disconnect()">Disconnect</button>
	    `
})
export class LogComponent implements OnInit {
  @Input() transitionId: number = 0;
  private logMessages: LogMessage[] = new Array();
  private ctrlMessage = {
      id: this.transitionId,
      message: '',
  }

  constructor(private logService: LogService) {
    logService.logMessages.subscribe(msg => {
      this.logMessages.push(msg);
    });
  }

  ngOnInit() {
  }

  connect() {
    this.ctrlMessage.message = 'connect';
    this.logService.logMessages.next(this.ctrlMessage);
  } 
  
  disconnect() {
    this.ctrlMessage.message = 'disconnect';
    this.logService.logMessages.next(this.ctrlMessage);

  }
}
